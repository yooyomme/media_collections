from typing import List
import uuid
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession


from app import security, database
from app.api.dependencies import get_current_user, get_current_admin, get_current_superuser
from app.models import User
from app.schemas.users import UserCreateSchema, UserResponseSchema, Token, UserLoginSchema, UserPermissionsInSchema, \
    UserUpdateSchema
from app.crud import users
from app.loggers import debug_logger


router = APIRouter(prefix="/users", tags=["👤 Users"])


@router.post("/register", response_model=UserResponseSchema, summary="Зарегистрироваться")
async def register_user(user: UserCreateSchema,
                        db: AsyncSession = Depends(database.get_db)):
    user_exists = await users.find_user_by_email(db, str(user.email))
    if user_exists:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    new_user = await users.create_user(db, user)
    return new_user


@router.post("/login", response_model=Token, summary="Войти в аккаунт")
async def login_user(user_data: UserLoginSchema,
                     db: AsyncSession = Depends(database.get_db)):
    user = await users.get_user_by_email(db, str(user_data.email))
    if (not user) or (not security.verify_password(user_data.password, user.hashed_password)):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    try:
        access_token = security.create_access_token(data={"sub": user.email})
        refresh_token = security.create_refresh_token(data={"sub": user.email})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        debug_logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера при генерации токенов")


@router.post("/token/refresh", response_model=Token, summary="Обновить access token")
async def refresh_access_token(refresh_token: str,
                               db: AsyncSession = Depends(database.get_db)):
    try:
        email = security.verify_refresh_token(token=refresh_token)
        user = await users.get_user_by_email(db, email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = security.create_access_token(data={"sub": user.email})
        new_refresh_token = security.create_refresh_token(data={"sub": user.email})

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        debug_logger.error(e)
        raise HTTPException(status_code=400, detail="Incorrect refresh token")


@router.get("/all", response_model=List[UserResponseSchema], summary="Получить всех пользователей", description="Admin only. For editing and testing.")
async def get_all_users(db: AsyncSession = Depends(database.get_db),
                        admin: User = Depends(get_current_admin)):
    users_list = await users.get_users(db)
    return users_list


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
    if str(user.id) != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    user = await users.update_user(db, user_id=user_id, data=data)
    return user


@router.delete("/{user_id}", status_code=204, summary="Удалить учетную запись")
async def delete_user_by_id(user_id: uuid.UUID,
                            db: AsyncSession = Depends(database.get_db),
                            user: User = Depends(get_current_user)):
    if str(user.id) != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    user = await users.delete_user(db, user_id=user_id)
    return user


@router.patch("/{user_id}/grant_permissions", response_model=UserResponseSchema, summary="Выдать или забрать права у пользователя", description="Admin only. For editing and testing.")
async def grant_permissions_for_user(user_id: uuid.UUID,
                                     data: UserPermissionsInSchema,
                                     db: AsyncSession = Depends(database.get_db),
                                     superuser: User = Depends(get_current_superuser)):
    result = await users.update_user(db, user_id=user_id, data=data)
    return result