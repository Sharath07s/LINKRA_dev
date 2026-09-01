from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.graph import PotentialLinkResponse
from app.ai.neo4j.predictions import neo4j_predictions

router = APIRouter()

@router.get("/{entity_id}", response_model=PotentialLinkResponse)
def get_potential_links_for_entity(
    entity_id: str,
    limit: int = Query(20, ge=1, le=50),
    min_score: float = Query(0.4, ge=0.0, le=1.0),
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get structural potential links for a specific entity.
    Requires an authenticated user.
    """
    try:
        result = neo4j_predictions.get_potential_links_for_entity(
            entity_id=entity_id, 
            limit=limit, 
            min_score=min_score
        )
        if result.get("status") == "not_found":
            raise HTTPException(status_code=404, detail=result.get("reason", "Entity not found"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch potential links: {str(e)}")
