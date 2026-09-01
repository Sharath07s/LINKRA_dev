from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.graph import AnomalyResponse
from app.ai.neo4j.anomaly import neo4j_anomaly

router = APIRouter()

@router.get("/top", response_model=AnomalyResponse)
def get_top_anomalies(
    limit: int = 50,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get top global structural anomalies from the graph.
    Requires an authenticated user.
    """
    # Enforce bounds
    if limit > 200:
        limit = 200
        
    try:
        return neo4j_anomaly.get_top_anomalies(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch anomalies: {str(e)}")

@router.get("/{entity_id}", response_model=AnomalyResponse)
def get_anomalies_for_entity(
    entity_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get structural anomalies for a specific entity.
    """
    try:
        result = neo4j_anomaly.get_anomalies_for_entity(entity_id=entity_id)
        if result.get("status") == "not_found":
            raise HTTPException(status_code=404, detail=result.get("reason", "Entity not found"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch entity anomalies: {str(e)}")
