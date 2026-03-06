import uuid
from typing import List, Annotated
from fastapi import Response, APIRouter, Depends, HTTPException, status, Cookie, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import security, database
from app.api.dependencies import get_current_user, get_current_admin, get_current_superuser, \
    get_current_collection_member
from app.utils import process_and_save_image, delete_image
from app.models import User
from app.schemas.collections import CollectionResponseSchema
from app.schemas.mediaitems import MediaItemResponseSchema, MediaItemInCollectionResponseSchema
from app.schemas.users import UserCreateSchema, UserResponseSchema, Token, UserLoginSchema, UserPermissionsInSchema, \
    UserUpdateSchema
from app.crud import users, collections
from app.loggers import debug_logger

CollectionResponseSchema.model_rebuild()


router = APIRouter(prefix="/users", tags=["👤 Users"])

refresh_cookie_data = {
    "key": "refresh_token",
    "value": None,
    "httponly": True,
    "secure": False,  # True для https
    "samesite": "lax",
    "max_age": 60 * 60 * 24 * 7  # 7 дней
}

def set_refresh_token_cookie(response: Response, refresh_token: str):
    set_cookie_data = refresh_cookie_data.copy()
    set_cookie_data["value"] = refresh_token
    response.set_cookie(**set_cookie_data)

def get_tokens_response(access_token: str):
    return {
        "access_token": access_token,
        "refresh_token": "stored_in_cookie",
        "token_type": "bearer"
    }


@router.post("/register", response_model=UserResponseSchema, summary="Зарегистрироваться")
async def register_user(user: UserCreateSchema,
                        db: AsyncSession = Depends(database.get_db)):
    user_exists = await users.find_user_by_email(db, str(user.email))
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    new_user = await users.create_user(db, user)
    return new_user


@router.post("/login", response_model=Token, summary="Войти в аккаунт")
async def login_user(user_data: UserLoginSchema,
                     response: Response,
                     db: AsyncSession = Depends(database.get_db)):
    user = await users.get_user_by_email(db, str(user_data.email))
    if (not user) or (not security.verify_password(user_data.password, user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    try:
        access_token = security.create_access_token(data={"sub": user.email})
        refresh_token = security.create_refresh_token(data={"sub": user.email})
        # для проверки работоспособности refresh токена можно вывести его в логи контейнера бэкенда:
        # debug_logger.warning(f"Для пользователя #{user.id} refresh token: {refresh_token}")
        # refresh токен устанавливается только в http-only cookie и не записывается в response
        set_refresh_token_cookie(response, refresh_token)
        return get_tokens_response(access_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера при генерации токенов")


@router.post("/token/refresh", response_model=Token, summary="Обновить access token")
async def refresh_access_token(refresh_token: Annotated[str | None, Cookie()] = None,
                               db: AsyncSession = Depends(database.get_db)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    try:
        email = security.verify_refresh_token(token=refresh_token)
        user = await users.get_user_by_email(db, email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        new_access_token = security.create_access_token(data={"sub": user.email})
        new_refresh_token = security.create_refresh_token(data={"sub": user.email})
        response_data = get_tokens_response(new_access_token)
        # для проверки работоспособности refresh токена можно вывести его в логи контейнера бэкенда:
        # debug_logger.warning(f"Для пользователя #{user.id} refresh token: {refresh_token}")
        # refresh токен устанавливается только в http-only cookie и не записывается в response
        response = JSONResponse(content=response_data)
        set_refresh_token_cookie(response, new_refresh_token)
        return response
    except Exception as e:
        debug_logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Incorrect refresh token")


@router.post("/logout", status_code=status.HTTP_200_OK, summary="Выйти из аккаунта")
async def logout_user(response: Response):
    delete_cookie_data = refresh_cookie_data.copy()
    delete_cookie_data.pop("value", None)
    delete_cookie_data.pop("max_age", None)
    response.delete_cookie(**delete_cookie_data)
    return {"message": "Logged out"}


@router.get("/all", response_model=List[UserResponseSchema],
            summary="Получить всех пользователей", description="Admin only. For editing and testing.")
async def get_all_users(db: AsyncSession = Depends(database.get_db),
                        admin: User = Depends(get_current_admin)):
    users_list = await users.get_users(db)
    return users_list


@router.get("/get_info/me", summary="Информация о пользователе для фронтенда")
async def get_current_user_data(user: User = Depends(get_current_user)):
    username = user.username if user.username else "Аноним"
    avatar_url = user.avatar_url if user.avatar_url else None
    return {
        "id": str(user.id),
        "email": user.email,
        "username": username,
        "avatar_url": avatar_url,
    }


@router.get("/{user_id}", response_model=UserResponseSchema, summary="Получить пользователя по id")
async def get_user_by_id(user_id: uuid.UUID,
                         db: AsyncSession = Depends(database.get_db),
                         user: User = Depends(get_current_user)):
    user = await users.get_user_by_id(db, user_id)
    return user


@router.patch("/{user_id}", response_model=UserResponseSchema, summary="Редактировать данные учетной записи")
async def update_user_by_id(user_id: uuid.UUID,
                            data: UserUpdateSchema,
                            db: AsyncSession = Depends(database.get_db),
                            user: User = Depends(get_current_user)):
    user = await users.update_user(db, user_id=user_id, data=data)
    return user


@router.delete("/{user_id}",  status_code=status.HTTP_200_OK, summary="Удалить учетную запись")
async def delete_user_by_id(user_id: uuid.UUID,
                            db: AsyncSession = Depends(database.get_db),
                            user: User = Depends(get_current_user)):
    await users.delete_user(db, user_id=user_id)
    return {"message": "Account has been deleted"}


@router.post("/{user_id}/avatar", response_model=UserResponseSchema, summary="Поставить или поменять аватар")
async def update_avatar(user_id: uuid.UUID,
                        file: UploadFile = File(...),
                        db: AsyncSession = Depends(database.get_db),
                        user: User = Depends(get_current_user)):
    url = await process_and_save_image(file, "avatars")
    result = await users.set_userpic(db, user.id, url)
    return result

@router.delete("/{user_id}/avatar", summary="Удалить аватар")
async def delete_avatar(user_id: uuid.UUID,
                        db: AsyncSession = Depends(database.get_db),
                        user: User = Depends(get_current_user)):
    user_data = await users.get_user_by_id(db, user_id)
    if user_data.avatar_url:
        await delete_image(user_data.avatar_url)
    await users.delete_userpic(db, user_id=user_id)
    return {"status": "success"}


@router.patch("/{user_id}/grant_permissions", response_model=UserResponseSchema,
              summary="Выдать или забрать права у пользователя", description="Superuser only.")
async def grant_permissions_for_user(user_id: uuid.UUID,
                                     data: UserPermissionsInSchema,
                                     db: AsyncSession = Depends(database.get_db),
                                     superuser: User = Depends(get_current_superuser)):
    result = await users.update_user(db, user_id=user_id, data=data)
    return result


@router.get("/{user_id}/collections", response_model=List[CollectionResponseSchema],
            summary="Все коллекции, созданные пользователем")
async def get_all_user_collections(user_id: uuid.UUID,
                                   db: AsyncSession = Depends(database.get_db),
                                   user: User = Depends(get_current_user)):
    result = await collections.get_collections_by_author(db, user_id=user_id)
    return result


@router.get("/{user_id}/membership_collections", response_model=List[CollectionResponseSchema],
            summary="Все коллекции, в которых пользователь является участником")
async def get_all_membership_collections(user_id: uuid.UUID,
                                         db: AsyncSession = Depends(database.get_db),
                                         user: User = Depends(get_current_user)):
    result = await collections.get_membership_collections_for_user(db, user_id=user_id)
    return result