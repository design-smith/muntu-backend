from fastapi import APIRouter, Depends, HTTPException
from ..models.team import TeamMember, TeamInvite
from ..utils.auth import get_current_user
from ..database import db
from typing import List
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.get("/members")
async def get_team_members(current_user: dict = Depends(get_current_user)):
    try:
        # Check if user has an organization
        if not current_user.get("organization_id"):
            return {
                "members": [],
                "message": "Please complete organization setup in onboarding"
            }

        members = await db.users.find({
            "organization_id": current_user["organization_id"]
        }).to_list(None)

        return {
            "members": [
                {
                    "id": str(member["_id"]),
                    "email": member["email"],
                    "first_name": member.get("first_name", ""),
                    "last_name": member.get("last_name", ""),
                    "role": member.get("role", "member")
                }
                for member in members
            ]
        }
    except Exception as e:
        print(f"Error fetching team members: {str(e)}")
        return {"members": [], "error": str(e)}

@router.get("/invites")
async def get_team_invites(current_user: dict = Depends(get_current_user)):
    try:
        # Check if user has an organization
        if not current_user.get("organization_id"):
            return {
                "invites": [],
                "message": "Please complete organization setup in onboarding"
            }

        invites = await db.team_invites.find({
            "organization_id": current_user["organization_id"]
        }).to_list(None)

        return {
            "invites": [
                {
                    "id": str(invite["_id"]),
                    "email": invite["email"],
                    "status": invite["status"],
                    "created_at": invite["created_at"]
                }
                for invite in (invites or [])
            ]
        }
    except Exception as e:
        print(f"Error fetching team invites: {str(e)}")
        return {"invites": [], "error": str(e)}

@router.post("/invite")
async def invite_team_member(
    invite_data: dict,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if user has an organization
        if not current_user.get("organization_id"):
            raise HTTPException(
                status_code=400,
                detail="Please complete organization setup in onboarding"
            )

        # Create invite
        invite = {
            "email": invite_data["email"],
            "organization_id": current_user["organization_id"],
            "invited_by": str(current_user["_id"]),
            "status": "pending",
            "created_at": datetime.utcnow()
        }

        result = await db.team_invites.insert_one(invite)
        
        return {
            "id": str(result.inserted_id),
            "message": f"Invitation sent to {invite_data['email']}"
        }
    except Exception as e:
        print(f"Error creating team invite: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 