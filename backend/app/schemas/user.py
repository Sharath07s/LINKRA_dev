from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    badge_number: str = Field(..., min_length=3, max_length=20, pattern=r'^[A-Za-z0-9\-]+$')
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=15)
    is_active: Optional[bool] = True
    role_id: Optional[UUID] = None
    station_id: Optional[UUID] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserUpdate(UserBase):
    badge_number: Optional[str] = Field(None, min_length=3, max_length=20, pattern=r'^[A-Za-z0-9\-]+$')
    password: Optional[str] = Field(None, min_length=8, max_length=128)


class User(UserBase):
    id: UUID

    class Config:
        from_attributes = True
