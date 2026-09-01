from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.intent import IntentRequest
from app.ai.intents.engine import IntentEngine

router = APIRouter()

@router.post("/extract", response_model=Dict[str, Any])
def extract_intent_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    query_in: IntentRequest,
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
) -> Any:
    """
    Extract structured intent from user query.
    """
    result = IntentEngine.extract_intent(query_in.query)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to extract intent"))
        
    return result["intent_data"]
