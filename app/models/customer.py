from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

class CustomerBase(BaseModel):
    organization_id: str
    name: str
    email: EmailStr
    phone: str
    channels: List[Dict[str, str | bool]] = []  # [{type, identifier, verified}]
    tags: List[str] = []

class Customer(CustomerBase):
    id: str
    last_contact: Optional[datetime]
    created_at: datetime
    updated_at: datetime 