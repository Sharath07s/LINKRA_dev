from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class PointGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]

class CrimeProperties(BaseModel):
    crime_id: str
    fir_number: Optional[str] = None
    crime_type: Optional[str] = None
    district: Optional[str] = None
    station: Optional[str] = None
    occurrence_date: Optional[datetime] = None
    status: Optional[str] = None
    estimated_loss: Optional[float] = None
    title: Optional[str] = None

class StationProperties(BaseModel):
    station_id: str
    station_code: str
    station_name: str
    district: Optional[str] = None
    address: Optional[str] = None

class CrimeFeature(BaseModel):
    type: str = "Feature"
    geometry: PointGeometry
    properties: CrimeProperties

class StationFeature(BaseModel):
    type: str = "Feature"
    geometry: PointGeometry
    properties: StationProperties

class CrimeFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[CrimeFeature]

class StationFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[StationFeature]

class PolygonGeometry(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]] # [[[lon, lat], ...]]

class DensityProperties(BaseModel):
    cluster_id: int
    crime_count: int
    density_score: float

class DensityFeature(BaseModel):
    type: str = "Feature"
    geometry: PolygonGeometry
    properties: DensityProperties

class DensityFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[DensityFeature]
