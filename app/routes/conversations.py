from fastapi import APIRouter, Depends
from ..models.conversation import Conversation, ConversationBase
from ..utils.auth import get_current_user
from datetime import datetime
from fastapi import Request, HTTPException
from ..database import db

router = APIRouter()

@router.get("/", response_model=list[Conversation])
async def get_conversations(current_user: dict = Depends(get_current_user)):
    # Add conversations retrieval logic here
    return []

@router.post("/", response_model=Conversation)
async def create_conversation(
    conversation_data: ConversationBase,
    request: Request
):
    try:
        # Create conversation with all required fields
        conversation = {
            "organization_id": conversation_data.organization_id,
            "customer_id": conversation_data.customer_id,
            "assigned_to": {
                "assistant_id": conversation_data.assigned_to.get("assistant_id", ""),
                "team_member_id": conversation_data.assigned_to.get("team_member_id")
            },
            "channel": {
                "type": conversation_data.channel.get("type", ""),
                "identifier": conversation_data.channel.get("identifier", "")
            },
            "status": conversation_data.status or "active",
            "metrics": {
                "response_time": 0.0,
                "resolution_time": 0.0,
                "customer_satisfaction": None
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await db.conversations.insert_one(conversation)
        created_conversation = await db.conversations.find_one({"_id": result.inserted_id})
        if created_conversation:
            created_conversation["id"] = str(created_conversation["_id"])
            del created_conversation["_id"]
        return created_conversation

    except Exception as e:
        print(f"Create conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 