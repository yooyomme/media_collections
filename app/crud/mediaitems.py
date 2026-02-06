from typing import Union, List

from fastapi import HTTPException

from sqlalchemy import Select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app import security
from app.loggers import debug_logger
from app.models.mediaitems import MediaItem
from app.schemas.mediaitems import MediaItemResponseSchema, MediaItemInSchema

async def get_media_items(db: AsyncSession):
    try:
        media_items = await db.execute(Select(MediaItem))
        return media_items.scalars().all()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Media items not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_media_item(db: AsyncSession, item_id: int):
    try:
        media_items = await db.execute(Select(MediaItem).where(MediaItem.id == item_id))
        return media_items.scalar_one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Media item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def find_media_item_by_simkl_id(simkl_id: int, db: AsyncSession):
    try:
        media_item_exists = await db.execute(Select(MediaItem).where(MediaItem.simkl_id == simkl_id))
        if media_item_exists.scalars().first():
            return True
        else:
            return False
    except NoResultFound:
        return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def create_media_item(db: AsyncSession, data: MediaItemInSchema):
    try:
        media_item = MediaItem()
        data_for_create = data.model_dump()
        media_item_already_exists = await find_media_item_by_simkl_id(data_for_create.simkl_id, db)
        if media_item_already_exists:
            raise HTTPException(status_code=409, detail="Media item already exists")
        for key, value in data_for_create.items():
            setattr(media_item, key, value)
        db.add(media_item)
        await db.commit()
        await db.refresh(media_item)
        return media_item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_media_item(db: AsyncSession, item_id: int, data: MediaItemInSchema):
    try:
        existing_item = await db.execute(Select(MediaItem).where(MediaItem.id == item_id))
        item_for_update = existing_item.scalar_one()
        data_for_update = data.model_dump(exclude_unset=True)
        for key, value in data_for_update.items():
            setattr(item_for_update, key, value)
        await db.commit()
        await db.refresh(item_for_update)
        return item_for_update
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_media_item(db: AsyncSession, item_id: int):
    try:
        existing_item = await db.execute(Select(MediaItem).where(MediaItem.id == item_id))
        await db.delete(existing_item)
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))