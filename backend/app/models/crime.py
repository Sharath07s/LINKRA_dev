from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy import Uuid as UUID
from app.models.base import BaseModel
from geoalchemy2 import Geometry

class CrimeType(BaseModel):
    __tablename__ = "crime_types"
    name = Column(String(255), index=True)
    category = Column(String(255))
    ipc_sections = Column(Text)
    severity_level = Column(Integer)

class Crime(BaseModel):
    __tablename__ = "crimes"
    fir_number = Column(String(100), unique=True, index=True)
    crime_type_id = Column(UUID(as_uuid=True), ForeignKey("crime_types.id"), index=True)
    station_id = Column(UUID(as_uuid=True), ForeignKey("police_stations.id"))
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), index=True)
    
    title = Column(String(500))
    description = Column(Text)
    
    occurrence_date = Column(DateTime(timezone=True), index=True)
    reported_date = Column(DateTime(timezone=True))
    
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    location = Column(Geometry('POINT', srid=4326))
    
    status = Column(String(100))
    estimated_loss = Column(Numeric)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    crime_type = relationship("CrimeType")
    station = relationship("PoliceStation")
    district = relationship("District")
    
    status_history = relationship("CrimeStatusHistory", back_populates="crime")
    suspects = relationship("SuspectCrime", back_populates="crime")
    victims = relationship("VictimCrime", back_populates="crime")
    vehicles = relationship("CrimeVehicle", back_populates="crime")
    evidence = relationship("Evidence", back_populates="crime")
    investigations = relationship("Investigation", back_populates="crime")

class CrimeStatusHistory(BaseModel):
    __tablename__ = "crime_status_history"
    crime_id = Column(UUID(as_uuid=True), ForeignKey("crimes.id"))
    previous_status = Column(String(100))
    new_status = Column(String(100))
    
    crime = relationship("Crime", back_populates="status_history")
