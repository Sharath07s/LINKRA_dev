from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.api import deps
from app.models.user import User
from app.services.intelligence_fusion.fusion_engine import fusion_engine
from app.services.intelligence_fusion.correlation_engine import correlation_engine
from app.services.intelligence_fusion.decision_support import decision_support_engine
from app.services.intelligence_fusion.prioritization_engine import prioritization_engine

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/signals")
async def get_signals(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Dict[str, Any]:
    return fusion_engine.get_unified_signals(db)

@router.get("/correlations")
async def get_correlations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Dict[str, Any]:
    return correlation_engine.get_correlations(db)

@router.get("/priorities")
async def get_priorities(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Dict[str, Any]:
    return prioritization_engine.get_priorities(db)

@router.get("/recommendations")
async def get_recommendations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Dict[str, Any]:
    return decision_support_engine.get_recommendations(db)

@router.post("/briefing")
async def generate_briefing(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Dict[str, Any]:
    # Gathers real intelligence to feed an LLM
    signals = fusion_engine.get_unified_signals(db)
    if signals.get("status") == "insufficient_data":
        return signals

    return {
        "status": "success",
        "briefing": "AI Briefing based solely on collected signals. Real LLM integration would process the fusion output strictly without hallucinations.",
        "context_used": signals.get("signals", [])
    }
