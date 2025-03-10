from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AssistantMetrics(BaseModel):
    accuracy_rate: float = 0.0
    average_response_time: float = 0.0
    verification_rate: float = 0.0

class AssistantBase(BaseModel):
    name: str
    role: str  # 'support' | 'sales'
    description: Optional[str] = None
    profile_picture_url: Optional[str] = None
    channels: List[str] = []  # ['phone', 'email', 'whatsapp', 'instagram', 'messenger']
    duties: List[str] = []
    organization_id: str
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    is_active: bool = True
    metrics: AssistantMetrics = AssistantMetrics()  # Add default metrics

class Assistant(AssistantBase):
    id: str

class AssistantCreate(AssistantBase):
    pass

class AssistantUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    profile_picture_url: Optional[str] = None
    channels: Optional[List[str]] = None
    duties: Optional[List[str]] = None
    is_active: Optional[bool] = None 