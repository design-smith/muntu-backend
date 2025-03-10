from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ContactBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    notes: Optional[str] = None
    organization_id: str
    status: str = "active"
    type: str = "lead"  # 'lead' | 'customer'

class Contact(ContactBase):
    id: str
    created_at: datetime
    updated_at: datetime

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    notes: Optional[str] = None
    organization_id: str

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    type: Optional[str] = None 