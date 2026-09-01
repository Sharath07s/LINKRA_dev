from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User

from app.services.predictive_validation.forecast_validator import ForecastValidator
from app.services.predictive_validation.hotspot_validator import HotspotValidator
from app.services.predictive_validation.recidivism_validator import RecidivismValidator
from app.services.predictive_validation.network_growth_validator import NetworkGrowthValidator

router = APIRouter()

@router.get("/forecast")
def validate_forecast(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    val = ForecastValidator(db)
    return val.validate()

@router.get("/hotspots")
def validate_hotspots(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    val = HotspotValidator(db)
    return val.validate()

@router.get("/recidivism")
def validate_recidivism(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    val = RecidivismValidator(db)
    return val.validate()

@router.get("/networks")
def validate_networks(
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    val = NetworkGrowthValidator()
    return val.validate()

@router.get("/summary")
def get_validation_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Any:
    
    forecast_res = ForecastValidator(db).validate()
    hotspot_res = HotspotValidator(db).validate()
    recidivism_res = RecidivismValidator(db).validate()
    network_res = NetworkGrowthValidator().validate()
    
    # If ANY core engine has insufficient data, we reflect that the platform is missing historical depth.
    if forecast_res.get("status") == "insufficient_data":
        return {"status": "insufficient_data", "available_records": forecast_res.get("available_records"), "required_records": forecast_res.get("required_records"), "module": "forecast"}
        
    return {
        "status": "validated",
        "overall_status": "validated",
        "forecast_accuracy": forecast_res,
        "hotspot_accuracy": hotspot_res,
        "recidivism_accuracy": recidivism_res,
        "network_accuracy": network_res
    }
