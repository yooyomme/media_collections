import uuid

from fastapi import HTTPException
from sqlalchemy import Select, or_, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.loggers import debug_logger
from app.models import Category, MediaItemCollection, Vote
from app.models.mediaitems import MediaItem
from app.schemas.mediaitems import MediaItemInSchema
from app.services import simkl_api


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


async def search_media_by_category_and_title(db: AsyncSession, query: str, category_id: int):
    try:
        query_result = await db.execute(
            Select(MediaItem).join(Category).where(Category.id == category_id)
            .where(MediaItem.title_en.ilike(f"%{query}%")).limit(20)
        )
        res = query_result.scalars().all()
        return res
    except NoResultFound:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_or_create_media_item(db: AsyncSession, simkl_id: int, media_type: str):
    try:
        item_id_db = await db.execute(
            Select(MediaItem).where(MediaItem.simkl_id == simkl_id)
        )
        result = item_id_db.scalar_one_or_none()
        if not result:
            category_db = await db.execute(Select(Category).where(Category.slug == media_type))
            category = category_db.scalar_one_or_none()
            if not category:
                raise HTTPException(status_code=404, detail="Media item category not found")
            media_item_data = await simkl_api.get_simkl_media_details(simkl_id)
            if not media_item_data:
                raise HTTPException(status_code=404, detail="Media item not found")

            media_item_dict = media_item_data[0]
            if "title_en" in media_item_dict:
                title = media_item_dict["title_en"]
            else:
                title = media_item_dict["title"]

            new_item = MediaItem(
                simkl_id=simkl_id,
                title_en=title,
                category=category.id,
                year=media_item_dict["year"],
                poster=media_item_dict["poster"],
            )

            if "ep_count" in media_item_dict:
                new_item.ep_count = media_item_data["ep_count"]

            db.add(new_item)
            await db.commit()
            await db.refresh(new_item)
            return new_item
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def add_item_to_collection(db: AsyncSession, media_item_id: int, collection_id: uuid.UUID):
    try:
        relation_exists = await db.execute(
            Select(MediaItemCollection).where(
                MediaItemCollection.collection_id == collection_id,
                MediaItemCollection.media_item_id == media_item_id
            )
        )
        if relation_exists.scalar_one_or_none():
            return
        set_relations = MediaItemCollection(
            collection_id = collection_id,
            media_item_id = media_item_id,
        )
        db.add(set_relations)
        await db.commit()
        await db.refresh(set_relations)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def remove_item_from_collection(db: AsyncSession, media_item_id: int, collection_id: uuid.UUID):
    try:
        col_id = str(collection_id)
        vote_relations = await db.execute(
            Select(Vote).where(and_(
                Vote.collection_id == col_id,
                Vote.item_id == media_item_id,
            ))
        )
        vote = vote_relations.scalars().all()
        for v in vote:
            await db.delete(v)
        await db.commit()

        relation = await db.execute(
            Select(MediaItemCollection).where(and_(
                MediaItemCollection.collection_id == col_id,
                MediaItemCollection.media_item_id == media_item_id
            ))
        )
        relation_to_remove = relation.scalar_one()
        await db.delete(relation_to_remove)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))