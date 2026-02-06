from fastapi import HTTPException
from sqlalchemy import Select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app import security
from app.loggers import debug_logger
from app.models.categories import Category
from app.schemas.categories import CategoryInSchema, CategoryResponseSchema

async def get_categories(db: AsyncSession):
    try:
        categories_list = await db.execute(Select(Category))
        return categories_list.scalars().all()
    except NoResultFound:
        raise HTTPException(status_code=404)
    except Exception as e:
        raise e

async def get_category(db: AsyncSession, category_id: int):
    try:
        category_item = await db.execute(Select(Category).where(Category.id == category_id))
        return category_item.scalar_one()
    except NoResultFound:
        raise HTTPException(status_code=404)
    except Exception as e:
        raise e

async def create_category(db: AsyncSession, data: CategoryInSchema):
    try:
        category_item = Category(**data.model_dump())
        db.add(category_item)
        await db.commit()
        await db.refresh(category_item)
        return category_item
    except Exception as e:
        raise e

async def update_category(db: AsyncSession, category_id: int, data: CategoryInSchema):
    try:
        existing_category = await db.execute(Select(Category).where(Category.id == category_id))
        category_for_update = existing_category.scalar_one()
        data_for_update = data.model_dump(exclude_unset=True)
        for key, value in data_for_update.items():
            setattr(category_for_update, key, value)
        await db.commit()
        await db.refresh(category_for_update)
        return category_for_update
    except NoResultFound:
        raise HTTPException(status_code=404)
    except Exception as e:
        raise e

async def delete_category(db: AsyncSession, category_id: int):
    try:
        existing_category = await db.execute(Select(Category).where(Category.id == category_id))
        await db.delete(existing_category)
        await db.commit()
        return True
    except Exception as e:
        raise e