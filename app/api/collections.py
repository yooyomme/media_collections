from typing import List
import uuid
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession


from app import security, database
from app.api.dependencies import get_current_user, get_current_admin, get_current_superuser
from app.models import User
from app.models.collections import Collection
from app.schemas.collections import CollectionCreateSchema, CollectionResponseSchema
from app.schemas.mediaitems import MediaItemResponseSchema
from app.crud import collections
from app.loggers import debug_logger

CollectionResponseSchema.model_rebuild()

router = APIRouter(prefix="/collections", tags=["📌 Collections"])

@router.get("/", response_model=List[CollectionResponseSchema],
            summary="Все коллекции", description="Admin only. For testing and editing.")
async def get_collections(db: AsyncSession = Depends(database.get_db),
                          admin: User = Depends(get_current_admin)):
    collections_list = await collections.get_collections(db)
    return collections_list

@router.get("/{collection_id}", response_model=CollectionResponseSchema,
            summary="Одна коллекция", description="Admin only. For testing and editing.")
async def get_collection(collection_id: uuid.UUID,
                         db: AsyncSession = Depends(database.get_db),
                         admin: User = Depends(get_current_admin)):
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
                           user: User = Depends(get_current_user)):
    updated_collection = await collections.update_collection(db, collection_id, collection_data, user)
    return updated_collection

@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить коллекцию")
async def delete_collection(collection_id: uuid.UUID,
                            db: AsyncSession = Depends(database.get_db),
                            user: User = Depends(get_current_user)):
    collection_data = await collections.delete_collection(db, collection_id, user)
    return collection_data
