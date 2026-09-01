from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
import logging

from app.api import deps
from app.models.user import User
from app.ai.neo4j.analytics import neo4j_analytics
from app.schemas.graph import (
    DegreeAnalyticsResponse, 
    CentralityNode, 
    ShortestPathResponse,
    RelationshipDistributionItem,
    ComponentAnalyticsResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/degree/{entity_id}", response_model=DegreeAnalyticsResponse)
def get_entity_degree(
    entity_id: str,
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    """
    Get degree connectivity for a specific entity.
    """
    try:
        return neo4j_analytics.get_entity_degree(entity_id)
    except Exception as e:
        logger.error(f"Graph analytics error: {e}")
        raise HTTPException(status_code=500, detail="Error querying graph analytics")

@router.get("/centrality/degree", response_model=List[CentralityNode])
def get_degree_centrality(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
):
    """
    Get top connected entities (Degree Centrality). 
    Requires higher clearance.
    """
    try:
        return neo4j_analytics.get_degree_centrality(limit)
    except Exception as e:
        logger.error(f"Graph analytics error: {e}")
        raise HTTPException(status_code=500, detail="Error querying graph analytics")

@router.get("/shortest-path", response_model=ShortestPathResponse)
def get_shortest_path(
    source: str,
    target: str,
    max_depth: int = Query(4, ge=1, le=10),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    """
    Bounded shortest path between two entities.
    """
    try:
        return neo4j_analytics.get_shortest_path(source, target, max_depth)
    except Exception as e:
        logger.error(f"Graph analytics error: {e}")
        raise HTTPException(status_code=500, detail="Error querying graph analytics")

@router.get("/distribution/{entity_id}", response_model=List[RelationshipDistributionItem])
def get_relationship_distribution(
    entity_id: str,
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    """
    Distribution of edge types for a given entity.
    """
    try:
        return neo4j_analytics.get_relationship_distribution(entity_id)
    except Exception as e:
        logger.error(f"Graph analytics error: {e}")
        raise HTTPException(status_code=500, detail="Error querying graph analytics")

@router.get("/component/{entity_id}", response_model=ComponentAnalyticsResponse)
def get_local_component(
    entity_id: str,
    max_depth: int = Query(5, ge=1, le=10),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    """
    Bounded component size estimation.
    """
    try:
        return neo4j_analytics.get_local_component(entity_id, max_depth)
    except Exception as e:
        logger.error(f"Graph analytics error: {e}")
        raise HTTPException(status_code=500, detail="Error querying graph analytics")
