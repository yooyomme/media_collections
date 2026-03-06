import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.api.dependencies import get_current_user, get_current_collection_member
from app.loggers import debug_logger
from app.schemas.votes import VoteCreateSchema, VoteResponseSchema, VoteExtendedResponseSchema
from app.security import verify_password
from app.services.websockets import manager
from app.utils import process_and_save_image, delete_image
from app.models import User, MediaItemCollection, AccessCollectionType
from app.schemas.collections import CollectionCreateSchema, CollectionResponseSchema, CollectionSettingsUpdateSchema, \
    CollectionMemberResponseSchema, CollectionJoinSchema
from app.schemas.mediaitems import MediaItemAddSchema, MediaItemResponseSchema, MediaItemInCollectionResponseSchema
from app.schemas.users import UserShortResponseSchema
from app.crud import collections, mediaitems

CollectionResponseSchema.model_rebuild()
CollectionMemberResponseSchema.model_rebuild()

router = APIRouter(prefix="/collections", tags=["📌 Collections"])

@router.get("/", response_model=List[CollectionResponseSchema], summary="Все коллекции")
async def get_collections(db: AsyncSession = Depends(database.get_db)):
    collections_list = await collections.get_collections(db)
    return collections_list

@router.get("/{collection_id}", response_model=CollectionResponseSchema,
            summary="Одна коллекция")
async def get_collection(collection_id: uuid.UUID,
                         db: AsyncSession = Depends(database.get_db),
                         user: User = Depends(get_current_collection_member)):
    collection_data = await collections.get_collection(db, collection_id)
    return collection_data

@router.post("/", response_model=CollectionResponseSchema, summary="Создать коллекцию")
async def post_collection(collection_data: CollectionCreateSchema,
                          db: AsyncSession = Depends(database.get_db),
                          user: User = Depends(get_current_user)):
    new_collection = await collections.create_collection(db, collection_data, user)
    return new_collection

@router.patch("/{collection_id}", response_model=CollectionResponseSchema, summary="Редактировать коллекцию")
async def patch_collection(collection_id: uuid.UUID,
                           collection_data: CollectionCreateSchema,
                           db: AsyncSession = Depends(database.get_db),
                           user: User = Depends(get_current_collection_member)):
    updated_collection = await collections.update_collection(db, collection_id, collection_data)
    await manager.broadcast_update(collection_id, {
        "type": "COLLECTION_UPDATED",
        "action": "meta_info_updated"
    })
    return updated_collection

@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить коллекцию")
async def delete_collection(collection_id: uuid.UUID,
                            db: AsyncSession = Depends(database.get_db),
                            user: User = Depends(get_current_user)):
    collection_data = await collections.delete_collection(db, collection_id, user)
    return collection_data

@router.get("/{collection_id}/share", summary="Поделиться доступом к коллекции")
async def get_share_link(collection_id: uuid.UUID,
                         db: AsyncSession = Depends(database.get_db),
                         user: User = Depends(get_current_user)):
    invite_token = await collections.get_invite_token(db, collection_id, user)
    return {
        "invite_token": invite_token
    }

@router.post("/{collection_id}/join", summary="Присоединиться к чьей-то коллекции")
async def join_collection(collection_id: uuid.UUID,
                          data: CollectionJoinSchema,
                          db: AsyncSession = Depends(database.get_db),
                          user: User = Depends(get_current_user)):
    is_member = await collections.find_collection_member_or_owner(db, collection_id, user)
    if is_member:
        return {"status": "success", "detail": "Already joined"}
    collection = await collections.get_collection(db, collection_id)
    # is_collection_public = collection.is_public
    # if is_collection_public:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="PUBLIC_ACCESS")

    access_mode = collection.access_type

    if access_mode == AccessCollectionType.PRIVATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if access_mode in [AccessCollectionType.LINK,
                       AccessCollectionType.LINK_AND_PASSWORD]:
        if collection.invite_token != data.invite_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="INVALID_TOKEN")

    if access_mode in [AccessCollectionType.PASSWORD,
                       AccessCollectionType.LINK_AND_PASSWORD]:
        if not data.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PASSWORD_REQUIRED")

        if not verify_password(data.password, collection.password_hash):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="INVALID_PASSWORD")

    await collections.set_user_for_collection_member(db, collection_id, user)
    return {"status": "success"}


@router.get("/{collection_id}/rating_info", summary="Информация об оценках элементов коллекции от пользователя")
async def get_collection_rate_info_for_user(collection_id: uuid.UUID,
                                            db: AsyncSession = Depends(database.get_db),
                                            user: User = Depends(get_current_user)):
    data = await collections.get_user_rating_info_in_collection(db, collection_id, user)
    return data

@router.post("/{collection_id}/cover", summary="Добавить обложку коллекции",
             description="Корректно работает при загрузке через сайт (загрузка медиа-файла)")
async def add_cover_to_collection(collection_id: uuid.UUID,
                                  file: UploadFile = File(...),
                                  db: AsyncSession = Depends(database.get_db),
                                  user: User = Depends(get_current_collection_member)):
    collection_data = await collections.get_collection(db, collection_id)
    if collection_data.cover_image:
        await delete_image(collection_data.cover_image)

    url = await process_and_save_image(file, "covers", size=(800, 600))
    result = await collections.set_cover(db, collection_id, url)
    await manager.broadcast_update(collection_id, {
        "type": "COLLECTION_UPDATED",
        "action": "cover_added"
    })
    return result

@router.delete("/{collection_id}/cover", summary="Удалить обложку коллекции")
async def delete_collection_cover(collection_id: uuid.UUID,
                                  db: AsyncSession = Depends(database.get_db),
                                  user: User = Depends(get_current_collection_member)):
    collection_data = await collections.get_collection(db, collection_id)
    if collection_data.cover_image:
        await delete_image(collection_data.cover_image)
    await collections.delete_cover(db, collection_id)
    await manager.broadcast_update(collection_id, {
        "type": "COLLECTION_UPDATED",
        "action": "cover_removed"
    })
    return {"status": "success"}


@router.delete("/{collection_id}/items/{item_id}", summary="Удалить медиа из коллекции")
async def remove_item_from_collection(collection_id: uuid.UUID,
                                      item_id: int,
                                      db: AsyncSession = Depends(database.get_db),
                                      user: User = Depends(get_current_user)):
    result = await mediaitems.remove_item_from_collection(db, item_id, collection_id)
    await manager.broadcast_update(collection_id, {
        "type": "COLLECTION_UPDATED",
        "action": "item_deleted"
    })
    return {"success": result}


@router.post("/{collection_id}/items/{item_id}/rate", response_model=VoteExtendedResponseSchema, summary="Оценить медиа")
async def rate_item_in_collection(collection_id: uuid.UUID,
                                  vote_data: VoteCreateSchema,
                                  db: AsyncSession = Depends(database.get_db),
                                  user: User = Depends(get_current_collection_member)):
    result = await collections.set_vote_for_item_in_collection(db, vote_data, user)
    additional_info = await collections.update_item_rating(db, vote_data)
    result.user_rate = additional_info.user_rate
    result.average_rating = additional_info.average_rating
    result.votes_count = additional_info.votes_count
    await manager.broadcast_update(collection_id, {
        "type": "COLLECTION_UPDATED",
        "action": "item_rated"
    })
    return result


@router.patch("/{collection_id}/settings", response_model=CollectionResponseSchema, summary="Изменить настройки приватности коллекции")
async def update_collection_settings(collection_id: uuid.UUID,
                                     settings: CollectionSettingsUpdateSchema,
                                     db: AsyncSession = Depends(database.get_db),
                                     user: User = Depends(get_current_user)):
    result = await collections.update_collection_privacy_settings(db, collection_id, settings, user)
    return result

@router.patch("/{collection_id}/settings/reset_invite_token", summary="Изменить токен приглашения в коллекцию")
async def update_collection_invite_token(collection_id: uuid.UUID,
                                         db: AsyncSession = Depends(database.get_db),
                                         user: User = Depends(get_current_user)):
    result = await collections.reset_invite_token(db, collection_id, user)
    return result

@router.get("/{collection_id}/members", response_model=List[CollectionMemberResponseSchema], summary="Все участники коллекции")
async def get_all_collection_members(collection_id: uuid.UUID,
                                     db: AsyncSession = Depends(database.get_db),
                                     user: User = Depends(get_current_user)):
    result = await collections.get_all_collection_members(db, collection_id, user)
    return result


@router.delete("/{collection_id}/members", summary="Сбросить доступ у всех участников коллекции")
async def remove_collection_members(collection_id: uuid.UUID,
                                    db: AsyncSession = Depends(database.get_db),
                                    user: User = Depends(get_current_user)):
    await collections.reset_all_collection_members(db, collection_id, user)
    return {"status": "success"}


@router.delete("/{collection_id}/members/{member_id}", summary="Сбросить доступ у одного участника коллекции")
async def remove_collection_member(collection_id: uuid.UUID,
                                   member_id: uuid.UUID,
                                   db: AsyncSession = Depends(database.get_db),
                                   user: User = Depends(get_current_user)):
    await collections.reset_one_member(db, collection_id, member_id, user)
    return {"status": "success"}