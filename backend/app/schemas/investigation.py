from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class InvestigationResponse(BaseModel):
    id: UUID
    crime_id: Optional[UUID]
    priority: Optional[str]
    status: Optional[str]
    summary: Optional[str]
    started_at: Optional[datetime]

    class Config:
        from_attributes = True

class CanonicalEntityBase(BaseModel):
    id: UUID
    entity_type: str
    name: str

    class Config:
        from_attributes = True

class InvestigationEntityBase(BaseModel):
    investigation_id: UUID
    entity_id: UUID

class InvestigationEntityCreate(InvestigationEntityBase):
    pass

class InvestigationEntityResponse(InvestigationEntityBase):
    id: UUID
    created_at: datetime
    entity: CanonicalEntityBase

    class Config:
        from_attributes = True

class InvestigationWorkspaceResponse(BaseModel):
    investigation_id: str
    entities: List[InvestigationEntityResponse]
