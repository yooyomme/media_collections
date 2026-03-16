from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.api.dependencies import get_current_admin
from app.models import User
from app.schemas.categories import CategoryInSchema, CategoryResponseSchema
from app.crud import categories

router = APIRouter(prefix="/categories", tags=["🗂 Categories"])

@router.get("/", response_model=List[CategoryResponseSchema],
            summary="Все категории")
async def get_categories(db: AsyncSession = Depends(database.get_db)):
    categories_list = await categories.get_categories(db)
    return categories_list

@router.get("/{category_id}", response_model=CategoryResponseSchema,
            summary="Одна категория", description="Admin only. For testing and editing.")
async def get_category(category_id: int,
                       db: AsyncSession = Depends(database.get_db),
                       admin: User = Depends(get_current_admin)):
    category_data = await categories.get_category(db, category_id)
    return category_data

@router.post("/", response_model=CategoryResponseSchema,
             summary="Создать категорию", description="Admin only. For testing and editing.")
async def post_category(category_data: CategoryInSchema,
                        db: AsyncSession = Depends(database.get_db),
                        admin: User = Depends(get_current_admin)):
    new_category = await categories.create_category(db, category_data)
    return new_category

@router.patch("/{category_id}", response_model=CategoryResponseSchema,
              summary="Редактировать категорию", description="Admin only. For testing and editing.")
async def update_category(category_id: int,
                          category_data: CategoryInSchema,
                          db: AsyncSession = Depends(database.get_db),
                          admin: User = Depends(get_current_admin)):
    category_data = await categories.update_category(db, category_id, category_data)
    return category_data

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удалить категорию", description="Admin only. For testing and editing.")
async def delete_category(category_id: int,
                          db: AsyncSession = Depends(database.get_db),
                          admin: User = Depends(get_current_admin)):
    category_data = await categories.delete_category(db, category_id)
    return category_data