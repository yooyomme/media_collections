import uuid
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, collection_id: uuid.UUID):
        await websocket.accept()
        col_id = str(collection_id)
        if col_id not in self.active_connections:
            self.active_connections[col_id] = []
        self.active_connections[col_id].append(websocket)

    def disconnect(self, websocket: WebSocket, collection_id: str):
        col_id = str(collection_id)
        if col_id in self.active_connections:
            self.active_connections[col_id].remove(websocket)
            if not self.active_connections[col_id]:
                del self.active_connections[col_id]

    async def broadcast_update(self, collection_id: uuid.UUID, message: dict):
        col_id = str(collection_id)
        if col_id in self.active_connections:
            for connection in self.active_connections[col_id]:
                await connection.send_json(message)

manager = ConnectionManager()
