from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BusinessBase(BaseModel):
    name: str
    industry: str
    business_type: str  # 'service' | 'product' | 'both' | 'nonprofit'
    size: str
    website: Optional[str] = None
    socials: List[dict] = []  # [{platform: string, url: string}]
    address: str
    phone: str
    description: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    status: str = "active"

class Business(BusinessBase):
    id: str

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    business_type: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    socials: Optional[List[dict]] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None 