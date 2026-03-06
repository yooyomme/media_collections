import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.api.dependencies import get_current_admin
from app.loggers import debug_logger
from app.models import User
from app.services import simkl_api
from app.schemas.mediaitems import MediaItemInSchema, MediaItemResponseSchema, MediaAddRequestSchema
from app.crud import mediaitems, collections
from app.services.websockets import manager


router = APIRouter(prefix="/items", tags=["🎦 Media Items"])


@router.get("/", response_model=List[MediaItemResponseSchema],
            summary="Все фильмы, сериалы и аниме")
async def get_all_media_items(db: AsyncSession = Depends(database.get_db)):
    media_items_list = await mediaitems.get_media_items(db)
    return media_items_list


@router.post("/", response_model=MediaItemResponseSchema,
             summary="Создать запись о медиа контенте")
async def post_media_item(media_item: MediaItemInSchema, db: AsyncSession = Depends(database.get_db)):
    new_media_item = await mediaitems.create_media_item(db, media_item)
    return new_media_item


@router.get("/{item_id}", response_model=MediaItemResponseSchema,
            summary="Один фильм, сериал или аниме")
async def get_media_item_by_id(item_id: int, db: AsyncSession = Depends(database.get_db)):
    media_items_list = await mediaitems.get_media_item(db, item_id)
    return media_items_list


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


@router.get("/search/list", summary="Поиск медиа")
async def search_media(query: str,
                       category_id: int,
                       collection_id: uuid.UUID = None,
                       db: AsyncSession = Depends(database.get_db)):
    media_items_in_db = await mediaitems.search_media_by_category_and_title(db, query, category_id)
    media_items_from_api = await simkl_api.search_simkl_media(category_id, query)
    results = {}
    if media_items_from_api:
        for item in media_items_from_api:
            item_simkl_id = item.get("ids", {}).get("simkl_id")

            if item.get("title_en"):
                title = item.get("title_en")
            else:
                title = item.get("title")

            results[item_simkl_id] = {
                "title": title,
                "year": item.get("year"),
                "simkl_id": item_simkl_id,
                "in_db": False,
            }
    if media_items_in_db:
        for item in media_items_in_db:
            search_in_collection = await collections.find_item_in_collection(db, collection_id, item.id)
            results[item.simkl_id] = {
                "title": item.title_en,
                "year": item.year,
                "simkl_id": item.simkl_id,
                "in_db": True,
                "id": item.id,
                "already_in_collection": search_in_collection,
            }
    return list(results.values())

@router.post("/search/add", summary="Добавление медиа")
async def add_media_item(data: MediaAddRequestSchema, db: AsyncSession = Depends(database.get_db)):
    item = await mediaitems.get_or_create_media_item(db, data.simkl_id, data.media_type)
    await mediaitems.add_item_to_collection(db, item.id, data.collection_id)
    await manager.broadcast_update(data.collection_id, {
        "type": "COLLECTION_UPDATED",
        "action": "item_added"
    })
    return item