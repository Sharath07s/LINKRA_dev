from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Any
from app.services.streaming.streaming_manager import streaming_manager
from app.services.streaming.event_bus import event_bus
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.websocket("/ws/command-wall")
async def ws_command_wall(
    websocket: WebSocket,
    current_user: User = Depends(deps.get_ws_user),
):
    if not current_user:
        return
    await streaming_manager.connect(websocket, "command-wall")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        streaming_manager.disconnect(websocket, "command-wall")

@router.websocket("/ws/alerts")
async def ws_alerts(
    websocket: WebSocket,
    current_user: User = Depends(deps.get_ws_user),
):
    if not current_user:
        return
    await streaming_manager.connect(websocket, "alerts")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        streaming_manager.disconnect(websocket, "alerts")

@router.websocket("/ws/officer-workspace")
async def ws_officer_workspace(
    websocket: WebSocket,
    current_user: User = Depends(deps.get_ws_user),
):
    if not current_user:
        return
    await streaming_manager.connect(websocket, "officer-workspace")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        streaming_manager.disconnect(websocket, "officer-workspace")

@router.websocket("/ws/predictive")
async def ws_predictive(
    websocket: WebSocket,
    current_user: User = Depends(deps.get_ws_user),
):
    if not current_user:
        return
    await streaming_manager.connect(websocket, "predictive")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        streaming_manager.disconnect(websocket, "predictive")

@router.websocket("/ws/system-health")
async def ws_system_health(
    websocket: WebSocket,
    current_user: User = Depends(deps.get_ws_user),
):
    if not current_user:
        return
    # Here we could also check if current_user has ADMIN role, but get_ws_user just checks auth.
    # For a more robust approach we could add a role check for WS, but getting auth is the first step.
    # Let's check role for system-health
    from app.db.session import SessionLocal
    from app.models.user import Role
    
    db = SessionLocal()
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    db.close()
    
    if not role or role.name != "ADMIN":
        await websocket.close(code=4003, reason="Forbidden")
        return
        
    await streaming_manager.connect(websocket, "system-health")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        streaming_manager.disconnect(websocket, "system-health")

@router.get("/metrics")
def get_streaming_metrics(
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    return {
        "event_bus": event_bus.get_metrics(),
        "websockets": streaming_manager.get_metrics()
    }
