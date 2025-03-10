from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOrganization(BaseModel):
    organization_id: str
    role: str
    joined_at: datetime

class UserPreferences(BaseModel):
    theme: str = "light"
    language: str = "en"
    notifications: dict = {
        "email": True,
        "push": True,
        "desktop": True
    }

class User(UserBase):
    id: str
    status: str
    organizations: List[UserOrganization]
    preferences: UserPreferences
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    user: 'User'
    access_token: str
    token_type: str 