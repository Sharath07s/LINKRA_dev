import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.copilot import CopilotQuery, CopilotResponse
from app.ai.copilot.orchestrator import CopilotOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=CopilotResponse)
def copilot_chat(
    query_in: CopilotQuery,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    M1.13 AI Copilot Endpoint.
    Takes a natural language query, orchestrates bounded context retrieval from Postgres and Neo4j,
    and returns a strictly grounded response with structured provenance.
    """
    try:
        response = CopilotOrchestrator.handle_query(db, query_in)
        return response
    except Exception as e:
        logger.error(f"Copilot chat failed: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the Copilot request.")
