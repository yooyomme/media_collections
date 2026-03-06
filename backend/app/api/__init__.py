from fastapi import APIRouter, WebSocket

from app.services.websockets import manager
from app.loggers import debug_logger

from app.api.users import router as users_router
from app.api.mediaitems import router as mediaitems_router
from app.api.categories import router as categories_router
from app.api.collections import router as collections_router


main_router = APIRouter(prefix="/api")
main_router.include_router(users_router)
main_router.include_router(mediaitems_router)
main_router.include_router(categories_router)
main_router.include_router(collections_router)

websocket_router = APIRouter(prefix="/websocket")

@websocket_router.websocket("/collection/{collection_id}")
async def websocket_endpoint(websocket: WebSocket, collection_id: str):
    await manager.connect(websocket, collection_id)
    try:
        while True:
            data = await websocket.receive_text()
    except Exception as e:
        debug_logger.warning(e)
        manager.disconnect(websocket, collection_id)