from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Uuid as UUID
from app.models.base import BaseModel
from geoalchemy2 import Geometry

class District(BaseModel):
    __tablename__ = "districts"
    district_name = Column(String(100), index=True)
    district_code = Column(String(20), unique=True, index=True)
    
    stations = relationship("PoliceStation", back_populates="district")

class PoliceStation(BaseModel):
    __tablename__ = "police_stations"
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"))
    station_name = Column(String(255), index=True)
    station_code = Column(String(50), unique=True, index=True)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    location = Column(Geometry('POINT', srid=4326))
    address = Column(String)
    
    district = relationship("District", back_populates="stations")
    users = relationship("User", foreign_keys="[User.station_id]", primaryjoin="User.station_id==PoliceStation.id")
