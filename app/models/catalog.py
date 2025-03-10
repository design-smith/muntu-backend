from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class CatalogItemBase(BaseModel):
    organization_id: str
    name: str
    type: str  # product, service
    description: Dict[str, str] = {
        "short": "",
        "long": ""
    }
    pricing: Dict[str, str | float | None] = {
        "type": "fixed",  # fixed, hourly, range, quote
        "value": None,
        "min": None,
        "max": None,
        "unit": None
    }
    metadata: Dict = {
        "tags": [],
        "category": "",
        "custom_fields": {}
    }

class CatalogItem(CatalogItemBase):
    id: str
    status: str = "active"
    created_at: datetime
    updated_at: datetime 