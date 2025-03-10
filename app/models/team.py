from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

class TeamMemberMetrics(BaseModel):
    conversations_handled: int = 0
    average_response_time: float = 0.0
    customer_satisfaction: float = 0.0
    resolution_rate: float = 0.0

class TeamMemberBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: str  # 'owner' | 'admin' | 'agent'
    status: str = 'active'  # 'active' | 'invited' | 'inactive'
    job_title: Optional[str] = None
    profile_picture: Optional[str] = None
    organization_id: str
    joined_at: datetime
    metrics: TeamMemberMetrics = TeamMemberMetrics()
    last_active: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class TeamMember(TeamMemberBase):
    id: str

class TeamInviteBase(BaseModel):
    email: EmailStr
    role: str  # 'admin' | 'agent'
    organization_id: str
    status: str = 'pending'  # 'pending' | 'accepted' | 'expired'
    created_at: datetime
    expires_at: datetime

class TeamInvite(TeamInviteBase):
    id: str 