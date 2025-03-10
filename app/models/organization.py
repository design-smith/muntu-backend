from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    business_details: Dict[str, str | Dict] = {
        "address": "",
        "phone": "",
        "email": "",
        "timezone": "",
        "operating_hours": {}
    }
    settings: Dict[str, str | bool | float] = {
        "default_language": "en",
        "ai_confidence_threshold": 0.8,
        "verification_required": True
    }
    subscription: Dict[str, str | list] = {
        "plan": "free",
        "status": "active",
        "features": []
    }

class Organization(OrganizationBase):
    id: str
    created_at: datetime
    updated_at: datetime 