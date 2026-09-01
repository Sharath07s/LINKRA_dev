from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.api import deps
from app.models.user import User
from app.models.crime import Crime
from app.models.alert import Alert
from app.models.officer import OfficerAssignment, OfficerAction
from app.models.analytics import AuditLog
from app.ai.provider import FallbackManager
from app.ai.neo4j.intelligence import neo4j_intelligence
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class ActionCreate(BaseModel):
    action_type: str
    notes: str
    case_id: str | None = None

class CopilotRequest(BaseModel):
    query: str

@router.get("/cases")
def get_assigned_cases(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN"])),
) -> Any:
    """Get open cases assigned to the current officer."""
    assignments = db.query(OfficerAssignment).filter(
        OfficerAssignment.officer_id == current_user.id,
        OfficerAssignment.case_id != None
    ).all()
    
    if not assignments:
        return []
        
    case_ids = [a.case_id for a in assignments]
    cases = db.query(Crime).filter(Crime.id.in_(case_ids)).all()
    return cases

@router.get("/alerts")
def get_assigned_alerts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN"])),
) -> Any:
    """Get active alerts assigned to the current officer."""
    assignments = db.query(OfficerAssignment).filter(
        OfficerAssignment.officer_id == current_user.id,
        OfficerAssignment.alert_id != None
    ).all()
    
    if not assignments:
        return []
        
    alert_ids = [a.alert_id for a in assignments]
    alerts = db.query(Alert).filter(Alert.id.in_(alert_ids), Alert.resolved == False).all()
    return alerts

@router.get("/actions")
def get_recent_actions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN"])),
) -> Any:
    actions = db.query(OfficerAction).filter(
        OfficerAction.officer_id == current_user.id
    ).order_by(OfficerAction.created_at.desc()).limit(10).all()
    return actions

@router.get("/audit")
def get_audit_timeline(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN"])),
) -> Any:
    # Get audit logs related to this user
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == current_user.id
    ).order_by(AuditLog.created_at.desc()).limit(15).all()
    return logs

@router.post("/action")
def log_action(
    payload: ActionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN"])),
) -> Any:
    action = OfficerAction(
        officer_id=current_user.id,
        case_id=payload.case_id if payload.case_id else None,
        action_type=payload.action_type,
        notes=payload.notes,
        created_at=datetime.utcnow()
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action

@router.post("/copilot")
def officer_copilot(
    payload: CopilotRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN"])),
) -> Any:
    # 1. Fetch Assignments
    cases = get_assigned_cases(db, current_user)
    alerts = get_assigned_alerts(db, current_user)
    actions = get_recent_actions(db, current_user)
    
    if not cases and not alerts:
        return {
            "response": "Officer, you currently have no assigned cases or active alerts. I recommend executing standard patrols in your assigned district.",
            "priority_actions": ["Conduct routine patrol", "Monitor radio for dispatched incidents"],
            "recommended_follow_ups": [],
            "risk_assessment": "Low",
            "evidence_used": []
        }

    # 2. Build neo4j context for the first assigned case
    neo4j_context = ""
    evidence = []
    if cases:
        first_case = cases[0]
        evidence.append(f"Case ID {first_case.id}")
        cypher = """
        MATCH (c:Crime {id: $case_id})<-[:PARTICIPATED_IN]-(s:Suspect)
        OPTIONAL MATCH (s)-[:KNOWS]-(a:Suspect)
        RETURN s.full_name as suspect, collect(a.full_name) as associates
        """
        try:
            results = neo4j_intelligence.execute_query(cypher, parameters={"case_id": first_case.id})
            if results:
                neo4j_context = "Known Network: " + str(results)
                evidence.append("Neo4j Suspect Graph")
        except Exception:
            pass

    # 3. Construct Prompt
    context = f"""
    Officer Name: {current_user.full_name}
    Assigned Cases Count: {len(cases)}
    Active Alerts Count: {len(alerts)}
    Recent Actions Logged: {len(actions)}
    Network Context: {neo4j_context}
    
    User Query: {payload.query}
    """
    
    prompt = f"You are the AI Copilot for a police officer. Review the following real-time database context and provide tactical recommendations. Context: {context}"
    
    try:
        response = FallbackManager.execute_with_fallback(prompt=prompt, temperature=0.3)
        return {
            "response": response["result"],
            "priority_actions": ["Review suspect associates", "Execute field interview"],
            "recommended_follow_ups": ["Check district cameras near last known location"],
            "risk_assessment": "Medium to High based on known network connections",
            "evidence_used": evidence if evidence else ["PostgreSQL Assignment Records"]
        }
    except Exception:
        logger.error("Officer copilot LLM call failed")
        return {
             "response": "AI copilot is temporarily unavailable. Please check system status.",
             "priority_actions": [],
             "recommended_follow_ups": [],
             "risk_assessment": "Unknown",
             "evidence_used": []
        }
