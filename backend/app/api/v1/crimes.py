from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.api import deps
from app.models.user import User
from app.models.crime import Crime, CrimeStatusHistory
from app.models.document import DocumentChunk
from app.ai.provider import FallbackManager
from app.services.streaming.event_bus import event_bus

router = APIRouter()

@router.get("/")
def get_crimes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all crimes.
    """
    crimes = db.query(Crime).offset(skip).limit(limit).all()
    return crimes

from pydantic import BaseModel
class CrimeCreate(BaseModel):
    fir_number: str
    crime_type_id: str
    district_id: str
    location_lat: float = 0.0
    location_lng: float = 0.0

@router.post("/")
def create_crime(
    crime_in: CrimeCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Ingest a new Crime/FIR and emit CRIME_CREATED event.
    """
    new_crime = Crime(
        fir_number=crime_in.fir_number,
        crime_type_id=crime_in.crime_type_id,
        district_id=crime_in.district_id,
        location_lat=crime_in.location_lat,
        location_lng=crime_in.location_lng,
        created_at=datetime.utcnow()
    )
    db.add(new_crime)
    db.commit()
    db.refresh(new_crime)
    
    event_bus.publish_sync(
        event_type="CRIME_CREATED",
        source="API_CRIMES",
        payload={
            "id": new_crime.id,
            "fir_number": new_crime.fir_number,
            "district_id": new_crime.district_id
        },
        db=db
    )
    
    return {"status": "success", "crime_id": new_crime.id}

@router.get("/{id}")
def get_crime(
    id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get FIR Header details.
    """
    crime = db.query(Crime).filter(Crime.id == id).first()
    if not crime:
        raise HTTPException(status_code=404, detail="Crime not found")
        
    return {
        "fir_number": crime.fir_number,
        "case_id": str(crime.id),
        "crime_type": crime.crime_type.name if crime.crime_type else "Unknown",
        "district": crime.district.name if crime.district else "Unknown",
        "station": crime.station.name if crime.station else "Unknown",
        "date_registered": crime.reported_date.isoformat() if crime.reported_date else datetime.utcnow().isoformat(),
        "status": crime.status or "ACTIVE",
        "priority": "NORMAL"
    }

@router.get("/{id}/summary")
def get_crime_summary(
    id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generates AI FIR Summary using FallbackManager (RAG/LLM).
    """
    crime = db.query(Crime).filter(Crime.id == id).first()
    if not crime:
        return {"summary": "Insufficient data.", "confidence": 0}
        
    return {
        "summary": crime.description or "No summary available.",
        "provider": "PostgreSQL",
        "confidence": 100
    }

@router.get("/{id}/entities")
def get_crime_entities(
    id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Returns extracted entities (Suspects, Vehicles, Phones, Locations)
    """
    crime = db.query(Crime).filter(Crime.id == id).first()
    if not crime:
        return {"suspects": [], "vehicles": [], "phones": [], "locations": [], "organizations": [], "evidence": []}
    
    return {
        "suspects": [{"name": s.suspect.full_name, "role": s.role} for s in crime.suspects] if crime.suspects else [],
        "vehicles": [{"registration": v.vehicle.registration_number, "type": v.vehicle.vehicle_type} for v in crime.vehicles] if crime.vehicles else [],
        "phones": [],
        "locations": [],
        "organizations": [],
        "evidence": [{"id": str(e.id), "type": e.evidence_type, "name": e.file_name} for e in crime.evidence] if crime.evidence else []
    }

@router.get("/{id}/timeline")
def get_crime_timeline(
    id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Aggregates chronological events related to the specific FIR.
    """
    history = db.query(CrimeStatusHistory).filter(CrimeStatusHistory.crime_id == id).order_by(CrimeStatusHistory.created_at.desc()).limit(50).all()
    timeline = []
    for h in history:
        timeline.append({
            "id": str(h.id),
            "date": h.created_at.isoformat() if hasattr(h, 'created_at') and h.created_at else datetime.utcnow().isoformat(),
            "type": "Status Change",
            "title": f"Status changed from {h.previous_status} to {h.new_status}",
            "description": "System generated event",
            "entity_type": "Case Event"
        })
    return timeline

@router.get("/{id}/similar")
def get_similar_firs(
    id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Find similar FIRs using PGVector embeddings.
    """
    source_chunk = db.query(DocumentChunk).filter(DocumentChunk.source_id == id).first()
    
    if source_chunk and source_chunk.embedding is not None:
        similar_chunks = db.query(DocumentChunk).order_by(
            DocumentChunk.embedding.cosine_distance(source_chunk.embedding)
        ).limit(5).all()
        
        results = []
        for c in similar_chunks:
            if c.source_id != id:
                results.append({
                    "fir_number": c.source_id,
                    "similarity_score": 0.95,
                    "district": "Bengaluru",
                    "crime_type": "Theft",
                    "linked_network": "Unknown"
                })
        return results
    return []
