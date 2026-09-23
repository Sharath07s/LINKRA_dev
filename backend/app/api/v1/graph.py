from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
import logging

from app.api import deps
from app.models.user import User
from app.models.investigation import InvestigationEntity
from sqlalchemy.orm import Session
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

@router.get("/search", response_model=GraphResponse)
def search_entities(
    q: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    """
    Search graph entities by name/ID and return a nodes list.
    """
    try:
        data = neo4j_intelligence.search_entities(q, limit=limit)
        return GraphResponse(
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            center_entity_id=None,
            total_nodes=len(data.get("nodes", [])),
            total_edges=len(data.get("edges", []))
        )
    except Exception as e:
        logger.error(f"Graph search error: {e}")
        raise HTTPException(status_code=500, detail="Error searching graph database")


@router.get("/investigations/{investigation_id}", response_model=GraphResponse)
def get_investigation_graph(
    investigation_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get the knowledge graph for a specific investigation.
    """
    try:
        # 1. Fetch the canonical entities associated with the investigation from Postgres
        investigation_entities = db.query(InvestigationEntity).filter(
            InvestigationEntity.investigation_id == investigation_id
        ).all()
        
        entity_ids = [str(ie.entity_id) for ie in investigation_entities]
        
        if not entity_ids:
            return GraphResponse(
                nodes=[],
                edges=[],
                center_entity_id=None,
                total_nodes=0,
                total_edges=0
            )
            
        # 2. Query Neo4j for the subgraph containing ONLY these entities
        data = neo4j_intelligence.get_subgraph_for_entities(entity_ids)
        
        return GraphResponse(
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            center_entity_id=None,
            total_nodes=len(data.get("nodes", [])),
            total_edges=len(data.get("edges", []))
        )
    except Exception as e:
        logger.error(f"Graph investigation query error: {e}")
        raise HTTPException(status_code=500, detail="Error querying graph database for investigation")

