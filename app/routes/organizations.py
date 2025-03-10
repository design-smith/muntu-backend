from fastapi import APIRouter, Depends, HTTPException, Body, Request
from ..models.organization import Organization, OrganizationBase
from ..models.business import Business, BusinessCreate
from ..utils.auth import get_current_user
from ..database import db
from datetime import datetime
from typing import Dict
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=list[Organization])
async def get_organizations(current_user: dict = Depends(get_current_user)):
    # Add organization retrieval logic here
    return [] 

@router.get("/current")
async def get_current_organization(current_user: dict = Depends(get_current_user)):
    try:
        # Check if user has an organization_id
        if not current_user.get("organization_id"):
            return {
                "message": "No organization found. Please complete onboarding.",
                "organization": None,
                "needs_onboarding": True
            }

        # Find organization
        organization = await db.organizations.find_one({"_id": ObjectId(current_user["organization_id"])})
        
        if not organization:
            return {
                "message": "Organization not found. Please complete onboarding.",
                "organization": None,
                "needs_onboarding": True
            }

        # Return organization data
        return {
            "organization": {
                "id": str(organization["_id"]),
                "name": organization.get("name", ""),
                "industry": organization.get("industry", ""),
                "size": organization.get("size", ""),
                "website": organization.get("website", ""),
                "created_at": organization.get("created_at", datetime.utcnow()),
                "updated_at": organization.get("updated_at", datetime.utcnow())
            },
            "needs_onboarding": False
        }
    except Exception as e:
        print(f"Error fetching organization: {str(e)}")
        return {
            "message": f"Error fetching organization: {str(e)}",
            "organization": None,
            "needs_onboarding": True
        }

@router.post("/")
async def create_organization(org_data: dict, current_user: dict = Depends(get_current_user)):
    try:
        # Create organization
        organization = {
            "name": org_data["name"],
            "industry": org_data.get("industry", ""),
            "size": org_data.get("size", ""),
            "website": org_data.get("website", ""),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "owner_id": current_user["_id"]
        }

        # Insert organization
        result = await db.organizations.insert_one(organization)
        organization_id = str(result.inserted_id)

        # Update user with organization_id
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {"organization_id": organization_id}}
        )

        return {
            "id": organization_id,
            "message": "Organization created successfully"
        }

    except Exception as e:
        print(f"Error creating organization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/current")
async def update_organization(
    org_data: dict,
    current_user: dict = Depends(get_current_user)
):
    try:
        if not current_user.get("organization_id"):
            raise HTTPException(
                status_code=404,
                detail="No organization found. Please complete onboarding."
            )

        # Update organization
        update_data = {
            "name": org_data.get("name"),
            "industry": org_data.get("industry"),
            "size": org_data.get("size"),
            "website": org_data.get("website"),
            "updated_at": datetime.utcnow()
        }

        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}

        result = await db.organizations.update_one(
            {"_id": ObjectId(current_user["organization_id"])},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Organization not found")

        return {"message": "Organization updated successfully"}

    except Exception as e:
        print(f"Error updating organization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 