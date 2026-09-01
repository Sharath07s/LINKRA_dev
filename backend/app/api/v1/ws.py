from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.api import deps
from app.models.user import User

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/notifications")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: User = Depends(deps.get_ws_user),
):
    """
    WebSocket endpoint for real-time notifications (e.g., new crimes, critical alerts).
    """
    if not current_user:
        return
        
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and wait for messages if needed
            data = await websocket.receive_text()
            await manager.broadcast(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
