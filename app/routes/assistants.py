from fastapi import APIRouter, Depends, HTTPException, Body, Request
from ..models.assistant import Assistant, AssistantCreate
from ..utils.auth import get_current_user
from ..database import db
from datetime import datetime
from typing import Dict
from bson import ObjectId

router = APIRouter()

@router.get("/")
async def get_assistants(current_user: dict = Depends(get_current_user)):
    try:
        # Check if user has an organization
        if not current_user.get("organization_id"):
            return {
                "assistants": [],
                "message": "Please complete organization setup in onboarding"
            }

        # Fetch assistants for the organization
        assistants = await db.assistants.find({
            "organization_id": current_user["organization_id"]
        }).to_list(None)

        # Format assistants for response
        formatted_assistants = [
            {
                "id": str(assistant["_id"]),
                "name": assistant.get("name", ""),
                "role": assistant.get("role", ""),
                "email": f"{assistant.get('name', '').lower()}.ai@muntu.ai",  # Generate AI email
                "phone": assistant.get("phone", ""),
                "status": assistant.get("status", "active"),
                "avatarUrl": assistant.get("profile_picture_url"),
                "channels": assistant.get("channels", []),
                "duties": assistant.get("duties", []),
                "description": assistant.get("description", ""),
                "metrics": assistant.get("metrics", {}),
                "created_at": assistant.get("created_at", datetime.utcnow()),
                "updated_at": assistant.get("updated_at", datetime.utcnow())
            }
            for assistant in assistants
        ]

        return {"assistants": formatted_assistants}

    except Exception as e:
        print(f"Error fetching assistants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Assistant)
async def create_assistant(
    assistant_data: AssistantCreate,
    request: Request
):
    try:
        # Create assistant with all required fields
        assistant = {
            "name": assistant_data.name,
            "role": assistant_data.role,
            "description": assistant_data.description or "",
            "profile_picture_url": assistant_data.profile_picture_url,
            "channels": assistant_data.channels or [],
            "duties": assistant_data.duties or [],
            "organization_id": assistant_data.organization_id,
            "status": "active",
            "is_active": True,
            "metrics": {
                "accuracy_rate": 0.0,
                "average_response_time": 0.0,
                "verification_rate": 0.0
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await db.assistants.insert_one(assistant)
        created_assistant = await db.assistants.find_one({"_id": result.inserted_id})
        if created_assistant:
            created_assistant["id"] = str(created_assistant["_id"])
            del created_assistant["_id"]
        return created_assistant

    except Exception as e:
        print(f"Create assistant error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 