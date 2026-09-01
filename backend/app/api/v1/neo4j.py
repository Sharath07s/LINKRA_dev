from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.db.neo4j import neo4j_conn
from app.ai.neo4j.intelligence import neo4j_intelligence
from pydantic import BaseModel
import logging
from app.api import deps
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

class CypherQuery(BaseModel):
    query: str
    parameters: Dict[str, Any] = None

@router.get("/health")
def neo4j_health(
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
) -> Dict[str, Any]:
    health_status = neo4j_conn.check_health()
    if health_status.get("status") != "healthy":
        raise HTTPException(status_code=503, detail="Database health check failed")
    return health_status

@router.get("/network/{suspect_id}")
def get_suspect_network(
    suspect_id: str,
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    return neo4j_intelligence.get_suspect_network(suspect_id)

@router.get("/crime/{crime_id}")
def get_crime_network(
    crime_id: str,
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    # Retrieve nodes/edges directly querying or add to intelligence
    return neo4j_intelligence.execute_query(
        "MATCH path = (c:Crime {id: $crime_id})-[*1..2]-(connected) UNWIND nodes(path) AS n UNWIND relationships(path) AS r RETURN collect(distinct n) AS nodes, collect(distinct r) AS edges",
        parameters={"crime_id": crime_id}
    )

@router.get("/vehicle/{vehicle_number}")
def get_vehicle_network(
    vehicle_number: str,
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    return neo4j_intelligence.find_crimes_by_vehicle(vehicle_number)

@router.get("/repeat-offenders")
def get_repeat_offenders(
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    return neo4j_intelligence.find_repeat_offenders()

@router.get("/high-risk-networks")
def get_high_risk_networks(
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "EXECUTIVE", "ADMIN"])),
):
    return neo4j_intelligence.get_high_risk_network()

@router.post("/query")
def execute_custom_query(
    payload: CypherQuery,
    current_user: User = Depends(deps.RoleChecker(["ADMIN"])),
):
    try:
        return neo4j_intelligence.execute_query(payload.query, payload.parameters)
    except Exception as e:
        logger.error(f"Cypher error: {e}")
        raise HTTPException(status_code=400, detail="Error executing Cypher query")
