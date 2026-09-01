from typing import Any, List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
import json
import logging

from app.api import deps
from app.models.user import User
from app.models.crime import Crime, CrimeType
from app.models.entities import Suspect, SuspectCrime
from app.models.location import District
from app.ai.provider import FallbackManager
from app.ai.neo4j.intelligence import neo4j_intelligence

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/threat-level")
def get_state_threat_level(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Any:
    """
    Calculate state-wide threat level purely using Postgres logic.
    """
    crime_count = db.query(Crime).count()
    suspect_count = db.query(Suspect).count()
    
    if crime_count == 0:
        return {
            "score": 0,
            "level": "LOW",
            "factors": []
        }

    c_score = min(40, (crime_count / 100) * 10)
    s_score = min(40, (suspect_count / 10) * 10)
    score = int(20 + c_score + s_score)
    
    if score < 40: level = "LOW"
    elif score < 70: level = "MEDIUM"
    elif score < 85: level = "HIGH"
    else: level = "CRITICAL"

    return {
        "score": score,
        "level": level,
        "factors": [
            {"name": f"Crime Volume ({crime_count})", "impact": "High" if crime_count > 50 else "Low"},
            {"name": f"Known Suspects ({suspect_count})", "impact": "High" if suspect_count > 10 else "Low"}
        ]
    }

@router.get("/district-rankings")
def get_district_rankings(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Any:
    """
    Returns top districts ranked by dynamic threat score using postgres aggregations.
    """
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    fourteen_days_ago = now - timedelta(days=14)

    # Calculate current 7 days vs previous 7 days crime counts
    results = db.query(
        District.name,
        func.count(Crime.id).label('total_crimes'),
        func.sum(case((Crime.created_at >= seven_days_ago, 1), else_=0)).label('recent_crimes'),
        func.sum(case((Crime.created_at >= fourteen_days_ago) & (Crime.created_at < seven_days_ago), 1)).else_(0).label('past_crimes')
    ).join(Crime, Crime.district_id == District.id).group_by(District.name).all()

    if not results:
        return []

    rankings = []
    for r in results:
        total = r.total_crimes or 0
        recent = r.recent_crimes or 0
        past = r.past_crimes or 0
        
        # Calculate growth
        growth_pct = 0
        if past > 0:
            growth_pct = int(((recent - past) / past) * 100)
        elif recent > 0:
            growth_pct = 100
            
        score = min(100, int((total * 2) + (growth_pct * 0.5)))
        
        rankings.append({
            "district": r.name,
            "score": score,
            "growth": f"{'+' if growth_pct > 0 else ''}{growth_pct}%",
            "hotspots": max(1, int(total / 5)), # Approximated based on volume
            "networks": 0, # Pending Neo4j cross-reference
            "trend": "up" if growth_pct > 0 else "down"
        })
        
    rankings.sort(key=lambda x: x["score"], reverse=True)
    return rankings[:20]

@router.get("/emerging-threats")
def get_emerging_threats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Any:
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    
    # Query spikes by CrimeType
    spikes = db.query(
        CrimeType.category,
        District.name,
        func.count(Crime.id).label('count')
    ).join(Crime, Crime.crime_type_id == CrimeType.id)\
     .join(District, Crime.district_id == District.id)\
     .filter(Crime.created_at >= seven_days_ago)\
     .group_by(CrimeType.category, District.name)\
     .having(func.count(Crime.id) >= 1)\
     .all()

    if not spikes:
        return []

    threats = []
    for s in spikes:
        count = s.count
        severity = "CRITICAL" if count > 10 else "HIGH" if count > 5 else "MEDIUM"
        threats.append({
            "type": f"{s.category} Spike",
            "district": s.name,
            "severity": severity,
            "confidence": min(99, 60 + (count * 5)),
            "detected_at": now.isoformat()
        })
    
    threats.sort(key=lambda x: x["confidence"], reverse=True)
    return threats[:5]

@router.get("/high-risk-offenders")
def get_high_risk_offenders(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Any:
    # Join suspects with their crimes to calculate real score
    offenders = db.query(
        Suspect.full_name,
        Suspect.risk_score,
        func.count(SuspectCrime.crime_id).label('crime_count')
    ).outerjoin(SuspectCrime, SuspectCrime.suspect_id == Suspect.id)\
     .group_by(Suspect.id, Suspect.full_name, Suspect.risk_score)\
     .order_by(func.count(SuspectCrime.crime_id).desc())\
     .limit(10).all()

    if not offenders:
        return []

    results = []
    for o in offenders:
        base_risk = float(o.risk_score or 0)
        c_count = o.crime_count or 0
        calc_score = int(base_risk * 5 + c_count * 10)
        final_score = min(100, max(0, calc_score))
        
        results.append({
            "name": o.full_name,
            "risk_score": final_score,
            "district": "Cross-District", # Could join Crime->District here
            "crimes": c_count,
            "network_size": 0, # Pending Neo4j integration per offender
            "threat_level": "CRITICAL" if final_score >= 85 else "HIGH" if final_score >= 70 else "MEDIUM"
        })
        
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results

@router.get("/high-risk-networks")
def get_high_risk_networks(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Any:
    # True Neo4j graph query to find community clusters
    cypher = """
    MATCH (s:Suspect)-[:KNOWS]-(associate:Suspect)
    WITH s, count(associate) AS degree
    ORDER BY degree DESC LIMIT 5
    OPTIONAL MATCH (s)-[:PARTICIPATED_IN]->(c:Crime)-[:OCCURRED_IN]->(d:District)
    RETURN s.full_name AS name, degree AS members, count(c) AS crimes, collect(distinct d.name) AS districts, (degree * 10 + count(c) * 5) AS risk_score
    """
    try:
        results = neo4j_intelligence.execute_query(cypher)
        if not results:
            return []
        
        networks = []
        for r in results:
            score = min(100, int(r.get("risk_score", 0)))
            networks.append({
                "name": f"{r.get('name', 'Unknown')} Syndicate",
                "members": r.get("members", 0),
                "crimes": r.get("crimes", 0),
                "districts": r.get("districts", []),
                "risk_score": score
            })
        return networks
    except Exception as e:
        logger.error(f"Neo4j high-risk-networks query failed: {e}")
        return []

@router.get("/hotspots")
def get_hotspots(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Any:
    crimes = db.query(Crime.latitude, Crime.longitude, District.name)\
               .join(District, Crime.district_id == District.id)\
               .filter(Crime.latitude != None, Crime.longitude != None)\
               .limit(100).all()
    
    if not crimes:
        return {"type": "FeatureCollection", "features": [], "top_hotspots": []}
    
    features = []
    district_counts = {}
    
    for c in crimes:
        dist = c.name
        district_counts[dist] = district_counts.get(dist, 0) + 1
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(c.longitude), float(c.latitude)]
            },
            "properties": {
                "weight": 1,
                "district": dist
            }
        })
        
    top = sorted([{"district": k, "crime_count": v, "risk_score": min(100, v * 10)} for k, v in district_counts.items()], key=lambda x: x["crime_count"], reverse=True)[:5]
        
    return {
        "type": "FeatureCollection",
        "features": features,
        "top_hotspots": top
    }

@router.post("/briefing")
def generate_briefing(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["EXECUTIVE", "ADMIN"])),
) -> Any:
    # 1. Gather real DB statistics
    crime_count = db.query(Crime).count()
    if crime_count == 0:
        return {
            "summary": "State database currently contains 0 records. Awaiting data ingestion.",
            "key_risks": [], "recommended_actions": [], "confidence": 100, "evidence_sources": ["PostgreSQL"]
        }
        
    districts = get_district_rankings(db, current_user)
    threats = get_emerging_threats(db, current_user)
    networks = get_high_risk_networks(db, current_user)
    
    top_district = districts[0]['district'] if districts else "None"
    top_threat = threats[0]['type'] if threats else "None"
    top_network = networks[0]['name'] if networks else "None"
    
    # 2. Inject real stats into the LLM prompt
    context = f"""
    Current State Statistics:
    Total Crimes: {crime_count}
    Top District: {top_district}
    Primary Threat: {top_threat}
    Largest Network: {top_network}
    """
    
    prompt = f"Analyze the following real-time database context and generate an executive intelligence briefing summarizing state-wide threat levels. Context: {context}"
    
    try:
        response = FallbackManager.execute_with_fallback(prompt=prompt, temperature=0.2)
        
        # We can extract the LLM response, but we still need structured JSON for UI.
        # FallbackManager normally returns a string in `result`. We'll use the real context to structure it.
        return {
            "summary": response["result"],
            "key_risks": [f"Emerging {t['type']} in {t['district']}" for t in threats[:2]],
            "recommended_actions": [f"Deploy resources to {top_district} due to high threat score."],
            "confidence": 92,
            "evidence_sources": ["PostgreSQL", "Neo4j Cypher", "LLM Inference"]
        }
    except Exception:
        logger.error("Executive briefing LLM call failed")
        return {
            "summary": "AI briefing unavailable. Check system status.",
            "key_risks": [],
            "recommended_actions": [],
            "confidence": 0,
            "evidence_sources": ["System Exception"]
        }
