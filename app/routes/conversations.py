from fastapi import APIRouter, Depends, HTTPException, Query
from ..models.conversation import Conversation, ConversationBase
from ..utils.auth import get_current_user
from datetime import datetime
from fastapi import Request
from ..database import db
from bson import ObjectId
from typing import Optional, List, Dict, Union

router = APIRouter()

@router.get("/", response_model=list[Conversation])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None
):
    try:
        # Build query filter
        query = {"organization_id": current_user["organization_id"]}
        if status:
            query["status"] = status

        # Fetch conversations with pagination
        conversations = await db.conversations.find(query)\
            .sort("updated_at", -1)\
            .skip(skip)\
            .limit(limit)\
            .to_list(length=limit)

        # Transform conversations
        transformed_conversations = []
        for conv in conversations:
            # Transform ObjectId to string
            conv["id"] = str(conv.pop("_id"))
            
            # Ensure assigned_to has the correct structure
            if "assigned_to" not in conv:
                conv["assigned_to"] = {
                    "assistant_id": "",
                    "team_member_id": None
                }
            elif isinstance(conv["assigned_to"], dict):
                conv["assigned_to"] = {
                    "assistant_id": conv["assigned_to"].get("assistant_id", ""),
                    "team_member_id": conv["assigned_to"].get("team_member_id")
                }
            
            # Get the last message for each conversation
            last_message = await db.messages.find_one(
                {"conversation_id": conv["id"]},
                sort=[("created_at", -1)]
            )
            
            if last_message:
                conv["last_message"] = {
                    "content": last_message["content"],
                    "created_at": last_message["created_at"]
                }

            # Get customer details if available
            if conv.get("customer_id"):
                customer = await db.customers.find_one({"_id": ObjectId(conv["customer_id"])})
                if customer:
                    conv["customer"] = {
                        "name": customer.get("name", "Unknown"),
                        "email": customer.get("email")
                    }
            
            # Ensure metrics exist
            if "metrics" not in conv:
                conv["metrics"] = {
                    "response_time": 0.0,
                    "resolution_time": 0.0,
                    "customer_satisfaction": None
                }
            
            transformed_conversations.append(conv)

        return transformed_conversations
    except Exception as e:
        print(f"Error fetching conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    before: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100)
):
    try:
        # Verify conversation exists and user has access
        conversation = await db.conversations.find_one({
            "_id": ObjectId(conversation_id),
            "organization_id": current_user["organization_id"]
        })
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Build query for messages
        query = {"conversation_id": conversation_id}
        if before:
            query["created_at"] = {"$lt": before}

        # Fetch messages with pagination
        messages = await db.messages.find(query)\
            .sort("created_at", -1)\
            .limit(limit)\
            .to_list(length=limit)

        # Transform messages
        for message in messages:
            message["id"] = str(message.pop("_id"))

        return messages[::-1]  # Reverse to get chronological order
    except Exception as e:
        print(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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