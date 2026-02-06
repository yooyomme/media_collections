from fastapi import HTTPException, Depends

from sqlalchemy import Select, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from sqlalchemy.orm import selectinload

from app import security
from app.loggers import debug_logger
from app.models import Collection, User
from app.schemas.collections import CollectionCreateSchema


async def get_collections(db: AsyncSession):
    try:
        collections_list = await db.execute(Select(Collection))
        return collections_list.scalars().all()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Media items not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_collection(db: AsyncSession, collection_id: uuid.UUID):
    try:
        collection_data = await db.execute(Select(Collection).where(Collection.id == collection_id))
        return collection_data.scalars().first()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Media items not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def create_collection(db: AsyncSession, collection_data: CollectionCreateSchema, user: User):
    try:
        data_for_dump = collection_data.model_dump(exclude={"media_items_id"})
        collection = Collection(**data_for_dump)
        if collection_data.media_items_id:
            for item_id in collection_data.media_items_id:
                collection.item_associations.append(item_id)
        db.add(collection)
        await db.commit()
        await db.refresh(collection)
        return collection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_collection(db: AsyncSession, collection_id: uuid.UUID, collection_data: CollectionCreateSchema, user: User):
    try:
        uid = str(user.id)
        existing_collection = await db.execute(Select(Collection).where(and_(Collection.id == collection_id, Collection.owner.id==uid)).options(selectinload(Collection.item_associations)))
        collection_for_update = existing_collection.scalar_one()
        data_for_update = collection_data.model_dump(exclude_unset=True)
        for key, value in data_for_update.items():
            setattr(collection_for_update, key, value)
        await db.commit()
        await db.refresh(collection_for_update)
        return collection_for_update
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Media items not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_collection(db: AsyncSession, collection_id: uuid.UUID, user: User):
    try:
        uid = str(user.id)
        existing_collection = await db.execute(Select(Collection).where(and_(Collection.id == collection_id, Collection.owner.id==uid)).options(selectinload(Collection.item_associations)))
        await db.delete(existing_collection)
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))