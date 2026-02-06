from typing import List
import uuid
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession


from app import security, database
from app.api.dependencies import get_current_user, get_current_admin, get_current_superuser
from app.models import User
from app.models.mediaitems import MediaItem
from app.schemas.mediaitems import MediaItemInSchema, MediaItemResponseSchema
from app.crud import mediaitems
from app.loggers import debug_logger

router = APIRouter(prefix="/items", tags=["🎦 Media Items"])

@router.get("/", response_model=List[MediaItemResponseSchema],
            summary="Все фильмы, сериалы и аниме")
async def get_all_media_items(db: AsyncSession = Depends(database.get_db)):
    media_items_list = await mediaitems.get_media_items(db)
    return media_items_list

@router.get("/{item_id}", response_model=MediaItemResponseSchema,
            summary="Один фильм, сериал или аниме")
async def get_media_item_by_id(item_id: int, db: AsyncSession = Depends(database.get_db)):
    media_items_list = await mediaitems.get_media_item(db, item_id)
    return media_items_list

@router.post("/", response_model=MediaItemResponseSchema,
             summary="Создать запись о медиа контенте")
async def post_media_item(media_item: MediaItemInSchema, db: AsyncSession = Depends(database.get_db)):
    new_media_item = await mediaitems.create_media_item(db, media_item)
    return new_media_item

@router.patch("/{item_id}", response_model=MediaItemResponseSchema,
              summary="Редактировать запись о медиа контенте", description="Admin only. For testing and editing.")
async def patch_media_item(item_id: int,
                           media_item: MediaItemInSchema,
                           db: AsyncSession = Depends(database.get_db),
                           admin: User = Depends(get_current_admin)):
    media_item = await mediaitems.update_media_item(db, item_id, media_item)
    return media_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удалить запись о медиа контенте", description="Admin only. For testing and editing.")
async def delete_media_item(item_id: int,
                            db: AsyncSession = Depends(database.get_db),
                            admin: User = Depends(get_current_admin)):
    media_item = await mediaitems.delete_media_item(db, item_id)
    return media_item