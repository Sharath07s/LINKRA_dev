from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User

from app.services.predictive_explainability.forecast_explainer import ForecastExplainer
from app.services.predictive_explainability.hotspot_explainer import HotspotExplainer
from app.services.predictive_explainability.recidivism_explainer import RecidivismExplainer
from app.services.predictive_explainability.network_growth_explainer import NetworkGrowthExplainer

router = APIRouter()

@router.get("/forecast")
def explain_forecast(
    district_id: str,
    crime_type_id: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    return ForecastExplainer(db).explain(district_id, crime_type_id)

@router.get("/hotspots")
def explain_hotspots(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    return HotspotExplainer(db).explain()

@router.get("/offenders/{suspect_id}")
def explain_offender(
    suspect_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    return RecidivismExplainer(db).explain(suspect_id)

@router.get("/networks")
def explain_networks(
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    return NetworkGrowthExplainer().explain()

@router.get("/summary")
def get_explainability_summary(
    district_id: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    # Need to pass a default district or handle iteration properly if None,
    # Here we simulate fetching explanations to pass to the frontend
    # Hardcoding a demo uuid if missing just to satisfy the API
    did = district_id or "00000000-0000-0000-0000-000000000000"
    
    fore = ForecastExplainer(db).explain(did)
    hot = HotspotExplainer(db).explain()
    net = NetworkGrowthExplainer().explain()
    
    if fore.get("status") == "insufficient_data" or hot.get("status") == "insufficient_data":
        return {"status": "insufficient_data"}
        
    return {
        "status": "success",
        "forecast_explainability": fore,
        "hotspot_explainability": hot,
        "network_explainability": net
    }
