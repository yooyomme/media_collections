from fastapi import APIRouter

from app.api.users import router as users_router
from app.api.mediaitems import router as mediaitems_router
from app.api.categories import router as categories_router
from app.api.collections import router as collections_router


main_router = APIRouter()
main_router.include_router(users_router)
main_router.include_router(mediaitems_router)
main_router.include_router(categories_router)
main_router.include_router(collections_router)