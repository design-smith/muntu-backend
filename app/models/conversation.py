from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ConversationBase(BaseModel):
    organization_id: str
    customer_id: str
    assigned_to: Dict[str, str] = {
        "assistant_id": "",
        "team_member_id": None
    }
    channel: Dict[str, str] = {
        "type": "",  # email, whatsapp, sms, messenger
        "identifier": ""
    }
    status: str = "active"  # active, resolved, pending

class ConversationMetrics(BaseModel):
    response_time: float = 0.0
    resolution_time: float = 0.0
    customer_satisfaction: Optional[float] = None

class Conversation(ConversationBase):
    id: str
    metrics: ConversationMetrics
    created_at: datetime
    updated_at: datetime 