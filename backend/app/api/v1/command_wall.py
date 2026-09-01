from typing import Any, List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.api import deps
from app.models.user import User
from app.models.crime import Crime
from app.models.alert import Alert
from app.models.officer import OfficerAction
from app.models.investigation import Investigation
from app.models.analytics import AuditLog
from app.models.entities import Suspect
from app.models.location import District
from app.ai.provider import FallbackManager
from app.ai.neo4j.intelligence import neo4j_intelligence

router = APIRouter()

@router.get("/threat-level")
def get_threat_level(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    crime_count = db.query(Crime).count()
    alert_count = db.query(Alert).filter(Alert.resolved == False).count()
    suspect_count = db.query(Suspect).count()
    
    if crime_count == 0 and alert_count == 0:
        return {"score": 0, "level": "LOW", "factors": []}
        
    c_score = min(40, (crime_count / 100) * 10)
    a_score = min(40, (alert_count / 10) * 10)
    s_score = min(20, (suspect_count / 50) * 5)
    
    score = int(c_score + a_score + s_score)
    if score < 40: level = "LOW"
    elif score < 70: level = "MEDIUM"
    elif score < 85: level = "HIGH"
    else: level = "CRITICAL"
    
    return {
        "score": score,
        "level": level,
        "factors": [
            f"Active Crimes: {crime_count}",
            f"Unresolved Alerts: {alert_count}",
            f"Known Suspects: {suspect_count}"
        ]
    }

@router.get("/alerts")
def get_alerts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return db.query(Alert).filter(Alert.resolved == False).order_by(Alert.created_at.desc()).limit(10).all()

@router.get("/hotspots")
def get_hotspots(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    results = db.query(
        District.name,
        func.count(Crime.id).label('count')
    ).join(Crime, Crime.district_id == District.id)\
     .group_by(District.name)\
     .order_by(func.count(Crime.id).desc())\
     .limit(5).all()
     
    return [{"district": r.name, "count": r.count} for r in results]

@router.get("/networks")
def get_networks(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    cypher = """
    MATCH (s:Suspect)-[:KNOWS]-(associate:Suspect)
    WITH s, count(associate) AS degree
    WHERE degree > 2
    RETURN s.full_name AS cluster_head, degree AS size
    ORDER BY size DESC LIMIT 5
    """
    try:
        results = neo4j_intelligence.execute_query(cypher)
        return [{"network": r.get("cluster_head", "Unknown"), "size": r.get("size", 0)} for r in results]
    except Exception:
        return []

@router.get("/officers")
def get_officers(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    now = datetime.utcnow()
    start_of_day = now.replace(hour=0, minute=0, second=0)
    
    active_count = db.query(func.count(func.distinct(OfficerAction.officer_id)))\
                     .filter(OfficerAction.created_at >= start_of_day).scalar() or 0
    actions_today = db.query(OfficerAction).filter(OfficerAction.created_at >= start_of_day).count()
    
    return {
        "active_officers": active_count,
        "actions_today": actions_today
    }

@router.get("/investigations")
def get_investigations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    active = db.query(Investigation).filter(Investigation.status == 'OPEN').count()
    high_priority = db.query(Investigation).filter(Investigation.priority == 'HIGH', Investigation.status == 'OPEN').count()
    return {
        "active": active,
        "high_priority": high_priority
    }

@router.get("/timeline")
def get_timeline(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # Blend of Audit Logs and Alerts
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(10).all()
    feed = []
    for l in logs:
        feed.append({
            "type": "SYSTEM",
            "message": f"{l.action} - {l.resource_type}",
            "timestamp": l.created_at
        })
    return sorted(feed, key=lambda x: x["timestamp"], reverse=True)[:10]

@router.post("/intelligence-feed")
def get_intelligence_feed(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Any:
    crime_count = db.query(Crime).count()
    if crime_count == 0:
         return {
            "findings": ["No intelligence generated. Awaiting database population."],
            "confidence": 100,
            "evidence": ["PostgreSQL"]
         }
         
    hotspots = get_hotspots(db, current_user)
    networks = get_networks(current_user)
    
    context = f"Total Crimes: {crime_count}, Hotspots: {hotspots}, Networks: {networks}"
    prompt = f"As the State Intelligence AI, generate a 2-sentence situational awareness briefing based on this live context: {context}"
    
    try:
        response = FallbackManager.execute_with_fallback(prompt=prompt, temperature=0.2)
        return {
            "findings": [response["result"]],
            "confidence": 95,
            "evidence": ["PostgreSQL Hotspots", "Neo4j Networks"]
        }
    except Exception:
        return {
            "findings": ["System intelligence synthesis unavailable."],
            "confidence": 0,
            "evidence": []
        }
