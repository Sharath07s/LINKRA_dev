from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User

from app.services.model_monitoring.forecast_monitor import ForecastMonitor
from app.services.model_monitoring.hotspot_monitor import HotspotMonitor
from app.services.model_monitoring.recidivism_monitor import RecidivismMonitor
from app.services.model_monitoring.network_monitor import NetworkMonitor
from app.services.model_monitoring.drift_detector import DriftDetector
from app.services.model_monitoring.monitoring_summary import MonitoringSummary

router = APIRouter()

@router.get("/forecast")
def monitor_forecast(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    return ForecastMonitor(db).monitor()

@router.get("/hotspots")
def monitor_hotspots(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    return HotspotMonitor(db).monitor()

@router.get("/recidivism")
def monitor_recidivism(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    return RecidivismMonitor(db).monitor()

@router.get("/networks")
def monitor_networks(
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    return NetworkMonitor().monitor()

@router.get("/drift")
def detect_drift(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    return DriftDetector(db).detect()

@router.get("/summary")
def get_monitoring_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    return MonitoringSummary(db).generate_summary()
