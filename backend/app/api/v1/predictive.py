import logging
from typing import Any, List, Dict

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.location import District
from app.services.predictive.crime_forecaster import CrimeForecaster
from app.services.predictive.hotspot_predictor import HotspotPredictor
from app.services.predictive.recidivism import RecidivismEngine
from app.services.predictive.network_growth import NetworkGrowthEngine
from app.ai.provider import FallbackManager
import json
from app.services.streaming.event_bus import event_bus

router = APIRouter()

@router.get("/forecast")
def get_forecast(
    district_id: str,
    crime_type_id: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    forecaster = CrimeForecaster(db)
    return forecaster.predict_volume(district_id, crime_type_id)

@router.get("/hotspots")
def get_hotspots(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    predictor = HotspotPredictor(db)
    return predictor.predict_hotspots()

@router.get("/offenders/{suspect_id}")
def get_offender_prediction(
    suspect_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    engine = RecidivismEngine(db)
    return engine.predict_recidivism(suspect_id)

@router.get("/networks")
def get_network_prediction(
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    engine = NetworkGrowthEngine()
    return engine.predict_growth()

@router.post("/briefing")
def generate_predictive_briefing(
    district_id: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    # 1. Gather all explainable predictive context
    from app.services.predictive_explainability.forecast_explainer import ForecastExplainer
    from app.services.predictive_explainability.hotspot_explainer import HotspotExplainer
    from app.services.predictive_explainability.network_growth_explainer import NetworkGrowthExplainer
    
    forecaster = ForecastExplainer(db)
    hotspot_predictor = HotspotExplainer(db)
    network_engine = NetworkGrowthExplainer()
    
    # We will grab forecasts for all districts or a specific one to feed the LLM
    districts = db.query(District).all()
    forecasts = []
    
    for d in (districts if not district_id else [db.query(District).get(district_id)]):
        if not d: continue
        res = forecaster.explain(str(d.id))
        if res.get("status") == "success":
            pred = res['prediction']
            exp = res['explainability']
            forecasts.append(f"{d.name}: Expected volume {pred['predicted_count']} ({pred['trend']}, Confidence Level: {exp['confidence_level']} | Score: {exp['confidence_score']} | Evidence: {exp['evidence']})")
            
    hotspots = hotspot_predictor.explain()
    hotspot_context = "No spatial escalation detected."
    if hotspots.get("status") == "success":
        hs_list = []
        for h in hotspots['hotspots']:
            exp = h['explainability']
            hs_list.append(f"District {h['district_id'][:8]} Confidence: {exp['confidence_level']} | Evidence: {exp['evidence']}")
        hotspot_context = " | ".join(hs_list)
        
    networks = network_engine.explain()
    network_context = "No structural expansion detected."
    if networks.get("status") == "success":
        net_list = []
        for n in networks['networks']:
            exp = n['explainability']
            net_list.append(f"Network {n['suspect_id'][:8]} Confidence: {exp['confidence_level']} | Evidence: {exp['evidence']}")
        network_context = " | ".join(net_list)
        
    # 2. Prevent Hallucination by strictly defining prompt
    prompt = f"""
    You are the KCIA Predictive Intelligence Synthesizer.
    Using ONLY the following statistical projections and computed confidence metrics, generate an executive predictive briefing.
    Do not hallucinate external evidence. Use only supplied predictive evidence and confidence metrics.
    
    FORECASTS:
    {chr(10).join(forecasts) if forecasts else 'Insufficient historical data for forecasting.'}
    
    HOTSPOTS:
    {hotspot_context}
    
    NETWORKS:
    {network_context}
    
    Format the response as JSON with:
    - "executive_summary": string
    - "key_risks": list of strings
    - "recommended_actions": list of strings
    """
    
    try:
        response_text = FallbackManager.execute_with_fallback(
            prompt=prompt,
            temperature=0.1
        )
        
        # Strip markdown if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
        data = json.loads(response_text)
        
        event_bus.publish_sync(
            event_type="PREDICTION_UPDATED",
            source="API_PREDICTIVE",
            payload={"briefing_generated": True},
            db=db
        )
        
        return {
            "status": "success",
            "briefing": data,
            "evidence": ["Data supplied by KCIA Predictive Engine", "Models: CrimeForecaster, HotspotPredictor, NetworkGrowthEngine"]
        }
    except Exception as e:
        logger.error(f"Predictive briefing generation failed: {e}")
        return {
            "status": "error",
            "message": "Failed to generate predictive briefing. Please try again."
        }
