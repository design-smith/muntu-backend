from fastapi import APIRouter, Depends, HTTPException, Body, Request
from ..models.user import User, UserUpdate
from ..utils.auth import get_current_user
from ..database import db
from datetime import datetime
from typing import Dict
from bson import ObjectId

router = APIRouter()

@router.get("/me", response_model=User)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    # Convert ObjectId to string for the id field
    current_user["id"] = str(current_user["_id"])
    return User(**current_user)

@router.put("/me", response_model=User)
async def update_user_profile(
    profile_data: UserUpdate,
    request: Request
):
    try:
        # Get current user from request state
        current_user = request.state.user
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Update user document
        update_data = {
            k: v for k, v in profile_data.dict().items() 
            if v is not None
        }
        
        if update_data:
            result = await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": update_data}
            )
            
            if not result.modified_count:
                raise HTTPException(status_code=404, detail="User not found")
                
        # Get updated user and format it properly
        updated_user = await db.users.find_one({"_id": current_user["_id"]})
        if updated_user:
            # Convert _id to string id
            updated_user["id"] = str(updated_user["_id"])
            del updated_user["_id"]
            # Make sure all required fields exist
            if "status" not in updated_user:
                updated_user["status"] = "active"
            if "organizations" not in updated_user:
                updated_user["organizations"] = []
            if "preferences" not in updated_user:
                updated_user["preferences"] = {
                    "theme": "light",
                    "language": "en",
                    "notifications": {
                        "email": True,
                        "push": True,
                        "desktop": True
                    }
                }
            if "updated_at" not in updated_user:
                updated_user["updated_at"] = datetime.utcnow()
            
        return updated_user
    except Exception as e:
        print(f"Update profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 