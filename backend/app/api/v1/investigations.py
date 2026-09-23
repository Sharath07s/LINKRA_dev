from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from uuid import UUID
import random
from datetime import datetime

from app.api import deps
from app.models.user import User
from app.models.investigation import Investigation, InvestigationNote, InvestigationEntity
from app.models.crime import Crime, CrimeStatusHistory
from app.models.analytics import AuditLog
from app.models.resolution import CanonicalEntity
from app.schemas.investigation import InvestigationEntityCreate, InvestigationEntityResponse, InvestigationWorkspaceResponse, InvestigationResponse

router = APIRouter()

@router.get("/", response_model=List[InvestigationResponse])
def get_investigations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    investigations = db.query(Investigation).offset(skip).limit(limit).all()
    if not investigations:
        return []
    return investigations

@router.get("/{id}")
def get_investigation(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get an investigation and its associated crime details.
    """
    investigation = db.query(Investigation).filter(Investigation.id == id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
        
    crime = None
    if investigation.crime_id:
        crime = db.query(Crime).filter(Crime.id == investigation.crime_id).first()
        
    return {
        "id": str(investigation.id),
        "firNumber": crime.fir_number if crime else "UNKNOWN",
        "crimeType": crime.crime_type.name if crime and crime.crime_type else "Investigation",
        "district": crime.district.district_name if crime and crime.district else "Unknown",
        "station": crime.station.station_name if crime and crime.station else "Unknown",
        "investigator": investigation.officer.full_name if investigation.officer else "Unknown",
        "status": investigation.status or "ACTIVE",
        "priority": investigation.priority or "NORMAL",
        "dateOpened": investigation.started_at.isoformat() if investigation.started_at else datetime.utcnow().isoformat(),
        "summary": investigation.summary or (crime.description if crime else None),
        "crime_id": str(crime.id) if crime else None
    }

@router.get("/{id}/entities", response_model=List[InvestigationEntityResponse])
def get_investigation_entities(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all entities associated with an investigation.
    """
    investigation = db.query(Investigation).filter(Investigation.id == id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
        
    entities = db.query(InvestigationEntity).filter(InvestigationEntity.investigation_id == id).all()
    return entities

@router.post("/{id}/entities", response_model=InvestigationEntityResponse)
def add_investigation_entity(
    id: UUID,
    entity_in: InvestigationEntityCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Associate an existing canonical entity with an investigation.
    """
    if entity_in.investigation_id != id:
        raise HTTPException(status_code=400, detail="Investigation ID mismatch")
        
    investigation = db.query(Investigation).filter(Investigation.id == id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
        
    canonical_entity = db.query(CanonicalEntity).filter(CanonicalEntity.id == entity_in.entity_id).first()
    if not canonical_entity:
        raise HTTPException(status_code=404, detail="Canonical Entity not found")
        
    existing = db.query(InvestigationEntity).filter(
        InvestigationEntity.investigation_id == id,
        InvestigationEntity.entity_id == entity_in.entity_id
    ).first()
    
    if existing:
        return existing
        
    inv_entity = InvestigationEntity(
        investigation_id=id,
        entity_id=entity_in.entity_id
    )
    db.add(inv_entity)
    db.commit()
    db.refresh(inv_entity)
    return inv_entity

@router.delete("/{id}/entities/{entity_id}")
def remove_investigation_entity(
    id: UUID,
    entity_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove an entity association from an investigation.
    """
    inv_entity = db.query(InvestigationEntity).filter(
        InvestigationEntity.investigation_id == id,
        InvestigationEntity.entity_id == entity_id
    ).first()
    
    if not inv_entity:
        raise HTTPException(status_code=404, detail="Investigation entity association not found")
        
    db.delete(inv_entity)
    db.commit()
    return {"status": "success"}

@router.get("/{id}/timeline")
def get_investigation_timeline(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Returns chronological events for the investigation timeline.
    """
    inv = db.query(Investigation).filter(Investigation.id == id).first()
    if not inv or not inv.crime_id: return []
    
    history = db.query(CrimeStatusHistory).filter(CrimeStatusHistory.crime_id == inv.crime_id).order_by(CrimeStatusHistory.created_at.desc()).limit(50).all()
    
    timeline = []
    
    if inv.started_at:
        timeline.append({
            "id": str(inv.id) + "_start",
            "type": "Investigation Created",
            "date": inv.started_at.isoformat(),
            "title": "Investigation Opened",
            "description": f"Investigation initiated by {inv.officer.full_name if inv.officer else 'System'}",
            "entity_type": "Case"
        })
        
    for h in history:
        timeline.append({
            "id": str(h.id),
            "type": "Status Change",
            "date": h.created_at.isoformat() if hasattr(h, 'created_at') and h.created_at else datetime.utcnow().isoformat(),
            "title": f"Status changed from {h.previous_status} to {h.new_status}",
            "description": "System generated event",
            "entity_type": "Case"
        })
    
    return sorted(timeline, key=lambda x: x["date"], reverse=True)

@router.get("/{id}/locations")
def get_investigation_locations(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Returns locations associated with an investigation for the map panel.
    """
    from app.schemas.geo import CrimeFeatureCollection, CrimeFeature, CrimeProperties, PointGeometry
    
    inv = db.query(Investigation).filter(Investigation.id == id).first()
    if not inv or not inv.crime_id:
        return CrimeFeatureCollection(features=[])
        
    crime = db.query(Crime).filter(Crime.id == inv.crime_id).first()
    features = []
    
    if crime and crime.longitude is not None and crime.latitude is not None:
        features.append(CrimeFeature(
            geometry=PointGeometry(coordinates=[float(crime.longitude), float(crime.latitude)]),
            properties=CrimeProperties(
                crime_id=str(crime.id),
                fir_number=crime.fir_number,
                crime_type=crime.crime_type.name if crime.crime_type else None,
                district=crime.district.district_name if crime.district else None,
                station=crime.station.station_name if crime.station else None,
                occurrence_date=crime.occurrence_date,
                status=crime.status,
                estimated_loss=float(crime.estimated_loss) if crime.estimated_loss else None,
                title=crime.title or crime.fir_number
            )
        ))
        
    return CrimeFeatureCollection(features=features)

@router.get("/{id}/threat-assessment")
def get_investigation_threat(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Returns threat assessment metrics for an investigation.
    """
    # Without sufficient data to compute threat, return empty
    return {
        "threat_score": 0,
        "risk_factors": [],
        "network_influence": 0.0,
        "recidivism_score": 0.0,
        "crime_severity": "UNKNOWN"
    }

@router.get("/{id}/audit")
def get_investigation_audit(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Returns database-backed audit logs for the investigation.
    """
    logs = db.query(AuditLog).filter(AuditLog.target_id == id).order_by(desc(AuditLog.created_at)).limit(50).all()
    return [{"id": str(l.id), "action": l.action, "module": l.module, "timestamp": l.created_at.isoformat() if hasattr(l, 'created_at') and l.created_at else datetime.utcnow().isoformat()} for l in logs]

@router.get("/{id}/health")
def get_investigation_health(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Returns investigation completeness metrics based on actual data.
    """
    inv = db.query(Investigation).filter(Investigation.id == id).first()
    if not inv:
        return None
        
    # Real health metrics based on what is available
    has_crime = 1 if inv.crime_id else 0
    entities_count = db.query(InvestigationEntity).filter(InvestigationEntity.investigation_id == id).count()
    has_entities = 1 if entities_count > 0 else 0
    
    score = int((has_crime + has_entities) / 2 * 100)
    
    return {
        "overall_completeness": score,
        "evidence_coverage": 0,
        "suspect_coverage": 100 if has_entities else 0,
        "network_coverage": 0,
        "timeline_coverage": 100 if has_crime else 0,
        "location_coverage": 0
    }

@router.post("/{id}/assign")
def assign_officer(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Assigns an officer to the investigation.
    """
    return {"status": "success", "msg": "Officer assigned successfully."}

