from fastapi import APIRouter

from app.api.users import router as users_router


main_router = APIRouter()
main_router.include_router(users_router)