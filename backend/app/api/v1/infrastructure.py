from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging

from app.api import deps
from app.models.user import User
from app.services.infrastructure.backup_manager import backup_manager
from app.services.infrastructure.recovery_manager import recovery_manager
from app.services.infrastructure.monitoring_manager import monitoring_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/metrics")
async def get_system_metrics(
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Dict[str, Any]:
    return monitoring_manager.get_system_metrics()

@router.get("/backups")
async def get_backup_status(
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Dict[str, Any]:
    return backup_manager.get_backup_status()

@router.post("/backups/trigger")
async def trigger_backup(
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Dict[str, Any]:
    return backup_manager.trigger_backup()

@router.get("/recovery")
async def get_recovery_status(
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Dict[str, Any]:
    return recovery_manager.get_recovery_status()
