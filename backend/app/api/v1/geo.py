from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from uuid import UUID

from app.api import deps
from app.models.user import User
from app.models.crime import Crime, CrimeType
from app.models.location import PoliceStation, District
from app.models.investigation import Investigation
from app.schemas.geo import CrimeFeatureCollection, CrimeFeature, CrimeProperties, PointGeometry
from app.schemas.geo import StationFeatureCollection, StationFeature, StationProperties
from app.schemas.geo import DensityFeatureCollection, DensityFeature, DensityProperties, PolygonGeometry
from sqlalchemy import text

router = APIRouter()

def parse_bbox(bbox: str) -> tuple[float, float, float, float]:
    try:
        parts = bbox.split(',')
        if len(parts) != 4:
            raise ValueError()
        min_lon, min_lat, max_lon, max_lat = map(float, parts)
        if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180 and -90 <= min_lat <= 90 and -90 <= max_lat <= 90):
            raise ValueError()
        if min_lon > max_lon or min_lat > max_lat:
            raise ValueError()
        return min_lon, min_lat, max_lon, max_lat
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid bbox format. Expected minLon,minLat,maxLon,maxLat")

@router.get("/filter-options")
def get_filter_options(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    districts = db.query(District).all()
    crime_types = db.query(CrimeType).all()
    
    # We query all investigations just in case there are some, though currently there are none.
    investigations = db.query(Investigation).all()
    
    return {
        "districts": [{"id": str(d.id), "name": d.district_name} for d in districts],
        "crime_types": [{"id": str(c.id), "name": c.name} for c in crime_types],
        "investigations": [{"id": str(i.id), "name": f"Investigation #{i.id}"} for i in investigations]
    }

@router.get("/crimes", response_model=CrimeFeatureCollection)
def get_geo_crimes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    bbox: Optional[str] = Query(None, description="Bounding box as minLon,minLat,maxLon,maxLat"),
    district_id: Optional[UUID] = None,
    crime_type_id: Optional[UUID] = None,
    investigation_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(500, le=2000)
) -> Any:
    query = db.query(Crime).filter(Crime.location.isnot(None))
    
    if bbox:
        min_lon, min_lat, max_lon, max_lat = parse_bbox(bbox)
        envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
        query = query.filter(func.ST_Intersects(Crime.location, envelope))
        
    if district_id:
        query = query.filter(Crime.district_id == district_id)
        
    if crime_type_id:
        query = query.filter(Crime.crime_type_id == crime_type_id)
        
    if investigation_id:
        query = query.filter(Crime.investigations.any(Investigation.id == investigation_id))
        
    if start_date:
        query = query.filter(Crime.occurrence_date >= start_date)
        
    if end_date:
        query = query.filter(Crime.occurrence_date <= end_date)
        
    crimes = query.limit(limit).all()
    
    features = []
    for c in crimes:
        if c.longitude is None or c.latitude is None:
            continue
            
        features.append(CrimeFeature(
            geometry=PointGeometry(coordinates=[float(c.longitude), float(c.latitude)]),
            properties=CrimeProperties(
                crime_id=str(c.id),
                fir_number=c.fir_number,
                crime_type=c.crime_type.name if c.crime_type else None,
                district=c.district.district_name if c.district else None,
                station=c.station.station_name if c.station else None,
                occurrence_date=c.occurrence_date,
                status=c.status,
                estimated_loss=float(c.estimated_loss) if c.estimated_loss else None,
                title=c.title
            )
        ))
        
    return CrimeFeatureCollection(features=features)

@router.get("/stations", response_model=StationFeatureCollection)
def get_geo_stations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    bbox: Optional[str] = Query(None, description="Bounding box as minLon,minLat,maxLon,maxLat"),
    limit: int = Query(500, le=1000)
) -> Any:
    query = db.query(PoliceStation).filter(PoliceStation.location.isnot(None))
    
    if bbox:
        min_lon, min_lat, max_lon, max_lat = parse_bbox(bbox)
        envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
        query = query.filter(func.ST_Intersects(PoliceStation.location, envelope))
        
    stations = query.limit(limit).all()
    
    features = []
    for s in stations:
        if s.longitude is None or s.latitude is None:
            continue
            
        features.append(StationFeature(
            geometry=PointGeometry(coordinates=[float(s.longitude), float(s.latitude)]),
            properties=StationProperties(
                station_id=str(s.id),
                station_code=s.station_code,
                station_name=s.station_name,
                district=s.district.district_name if s.district else None,
                address=s.address
            )
        ))
        
    return StationFeatureCollection(features=features)

@router.get("/crime-density", response_model=DensityFeatureCollection)
def get_crime_density(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    bbox: Optional[str] = Query(None, description="Bounding box as minLon,minLat,maxLon,maxLat"),
    district_id: Optional[UUID] = None,
    crime_type_id: Optional[UUID] = None,
    investigation_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Any:
    # Build dynamic WHERE clause based on filters
    where_clauses = ["crimes.location IS NOT NULL"]
    params = {}
    
    if bbox:
        min_lon, min_lat, max_lon, max_lat = parse_bbox(bbox)
        # We parameterize the ST_MakeEnvelope arguments using SQLAlchemy text parameters
        where_clauses.append("ST_Intersects(crimes.location, ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326))")
        params.update({"min_lon": min_lon, "min_lat": min_lat, "max_lon": max_lon, "max_lat": max_lat})
        
    if district_id:
        where_clauses.append("crimes.district_id = :district_id")
        params["district_id"] = str(district_id)
        
    if crime_type_id:
        where_clauses.append("crimes.crime_type_id = :crime_type_id")
        params["crime_type_id"] = str(crime_type_id)
        
    if investigation_id:
        where_clauses.append("EXISTS (SELECT 1 FROM investigations i WHERE i.crime_id = crimes.id AND i.id = :investigation_id)")
        params["investigation_id"] = str(investigation_id)
        
    if start_date:
        where_clauses.append("crimes.occurrence_date >= :start_date")
        params["start_date"] = start_date
        
    if end_date:
        where_clauses.append("crimes.occurrence_date <= :end_date")
        params["end_date"] = end_date
        
    where_sql = " AND ".join(where_clauses)
    
    # Use ST_ClusterDBSCAN to compute spatial density
    # eps is roughly 0.05 degrees (~5.5km), minpoints=5
    # Then group by cluster_id to compute the convex hull polygon of the cluster
    sql = text(f"""
        WITH clustered AS (
            SELECT location, ST_ClusterDBSCAN(location, eps := 0.05, minpoints := 5) OVER () AS cluster_id
            FROM crimes
            WHERE {where_sql}
        ),
        cluster_hulls AS (
            SELECT 
                cluster_id, 
                COUNT(*) as crime_count,
                ST_ConvexHull(ST_Collect(location)) as geom
            FROM clustered
            WHERE cluster_id IS NOT NULL
            GROUP BY cluster_id
        )
        SELECT 
            cluster_id,
            crime_count,
            ST_AsGeoJSON(geom) as geojson
        FROM cluster_hulls
        ORDER BY crime_count DESC
    """)
    
    results = db.execute(sql, params).fetchall()
    
    import json
    
    features = []
    for r in results:
        cluster_id = r.cluster_id
        crime_count = r.crime_count
        geom_json = json.loads(r.geojson)
        
        # In rare cases ST_ConvexHull of 2 identical points returns a Point/LineString. 
        # We ensure it's returned if it's a Polygon, or we handle it gracefully.
        if geom_json.get("type") == "Polygon":
            coords = geom_json.get("coordinates", [])
        else:
            # Skip non-polygons for density rendering (like identical points)
            continue
            
        features.append(DensityFeature(
            geometry=PolygonGeometry(coordinates=coords),
            properties=DensityProperties(
                cluster_id=cluster_id,
                crime_count=crime_count,
                density_score=float(crime_count) # simple density score
            )
        ))
        
    return DensityFeatureCollection(features=features)
