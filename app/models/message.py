from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class MessageBase(BaseModel):
    conversation_id: str
    sender: Dict[str, str] = {
        "type": "",  # customer, assistant, team
        "id": ""
    }
    content: Dict[str, str | Dict] = {
        "type": "text",  # text, image, file
        "body": "",
        "metadata": {}
    }

class Message(MessageBase):
    id: str
    status: str = "sent"  # sent, delivered, read
    ai_metadata: Optional[Dict] = None  # confidence, verified, verifiedBy
    created_at: datetime 