"""
Pydantic schemas for Client Profile
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class ClientProfileBase(BaseModel):
    """Base schema for client profile"""
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the client")
    company: str = Field(..., min_length=1, max_length=100, description="Company name")
    role: str = Field(..., min_length=1, max_length=100, description="Role/position in the company")
    email: Optional[str] = Field(None, max_length=150, description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")


class ClientProfileCreate(ClientProfileBase):
    """Schema for creating a client profile"""
    profile_key: str = Field(default="default_profile", max_length=50, description="Unique profile key")


class ClientProfileUpdate(BaseModel):
    """Schema for updating a client profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    company: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=50)


class ClientProfileResponse(ClientProfileBase):
    """Schema for client profile response"""
    id: int
    profile_key: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "profile_key": "default_profile",
                "name": "Kjell R. Christensen",
                "company": "DOF",
                "role": "Analyst",
                "email": "kjell@dof.no",
                "phone": "+47 123 45 678",
                "created_at": "2025-10-15T12:00:00Z",
                "updated_at": "2025-10-15T12:00:00Z"
            }
        }
