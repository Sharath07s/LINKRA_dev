from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
import logging

from app.api import deps
from app.models.user import User
from app.ai.neo4j.intelligence import neo4j_intelligence
from app.schemas.graph import GraphResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/entity/{entity_id}", response_model=GraphResponse)
def get_entity_node(
    entity_id: str,
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    """
    Get a single entity node and no relationships.
    """
    try:
        data = neo4j_intelligence.get_entity_neighborhood(entity_id, depth=0)
        return GraphResponse(
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            center_entity_id=entity_id,
            total_nodes=len(data.get("nodes", [])),
            total_edges=len(data.get("edges", []))
        )
    except Exception as e:
        logger.error(f"Graph query error: {e}")
        raise HTTPException(status_code=500, detail="Error querying graph database")


@router.get("/subgraph/{entity_id}", response_model=GraphResponse)
def get_entity_neighborhood(
    entity_id: str,
    depth: int = Query(1, ge=1, le=3),
    max_nodes: int = Query(50, ge=1, le=500),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    """
    Get an entity and its N-degree neighborhood relationships, bounded by max_nodes.
    """
    try:
        data = neo4j_intelligence.get_entity_neighborhood(entity_id, depth=depth, max_nodes=max_nodes)
        
        # If Neo4j is empty or entity not found, return an empty graph rather than a 404,
        # to ensure the UI can render gracefully.
        return GraphResponse(
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            center_entity_id=entity_id,
            total_nodes=len(data.get("nodes", [])),
            total_edges=len(data.get("edges", []))
        )
    except Exception as e:
        logger.error(f"Graph query error: {e}")
        raise HTTPException(status_code=500, detail="Error querying graph database")
