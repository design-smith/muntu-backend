from fastapi import APIRouter, Depends, HTTPException, Body, Request
from ..models.organization import Organization, OrganizationBase
from ..models.business import Business, BusinessCreate
from ..utils.auth import get_current_user
from ..database import db
from datetime import datetime
from typing import Dict
from bson import ObjectId
from ..models.user import UserCreate

router = APIRouter()

@router.get("/", response_model=list[Organization])
async def get_organizations(current_user: dict = Depends(get_current_user)):
    # Add organization retrieval logic here
    return [] 

@router.get("/current")
async def get_current_organization(current_user: dict = Depends(get_current_user)):
    try:
        # Find organization by owner_id instead of organization_id
        organization = await db.organizations.find_one({"owner_id": current_user["_id"]})
        
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
                "business_type": organization.get("business_type", ""),
                "size": organization.get("size", ""),
                "website": organization.get("website", ""),
                "phone": organization.get("phone", ""),
                "address": organization.get("address", ""),
                "description": organization.get("description", ""),
                "socials": organization.get("socials", []),
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
        print(f"Received organization data: {org_data}")
        print(f"Current user: {current_user}")
        
        # Validate required fields
        required_fields = ["name", "industry", "business_type", "size"]
        missing_fields = [field for field in required_fields if not org_data.get(field)]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )

        # Check if user already has an organization
        existing_org = await db.organizations.find_one({"owner_id": current_user["_id"]})
        if existing_org:
            print(f"User already has organization: {existing_org}")
            raise HTTPException(
                status_code=400,
                detail="User already has an organization"
            )

        # Create organization with current timestamp
        now = datetime.utcnow()
        organization = {
            "name": org_data["name"],
            "industry": org_data["industry"],
            "business_type": org_data["business_type"],
            "size": org_data["size"],
            "website": org_data.get("website", ""),
            "phone": org_data.get("phone", ""),
            "address": org_data.get("address", ""),
            "description": org_data.get("description", ""),
            "socials": org_data.get("socials", []),
            "created_at": now,
            "updated_at": now,
            "owner_id": current_user["_id"]
        }
        
        print(f"Attempting to create organization: {organization}")

        try:
            # Insert organization
            result = await db.organizations.insert_one(organization)
            organization_id = str(result.inserted_id)
            print(f"Organization created successfully with ID: {organization_id}")

            # Return the created organization in the same format as get_current_organization
            return {
                "organization": {
                    "id": organization_id,
                    "name": organization["name"],
                    "industry": organization["industry"],
                    "business_type": organization["business_type"],
                    "size": organization["size"],
                    "website": organization["website"],
                    "phone": organization["phone"],
                    "address": organization["address"],
                    "description": organization["description"],
                    "socials": organization["socials"],
                    "created_at": organization["created_at"],
                    "updated_at": organization["updated_at"]
                },
                "needs_onboarding": False
            }
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            print(f"Error type: {type(db_error)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")

    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        print(f"Error creating organization: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/current")
async def update_organization(
    org_data: dict,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Find organization by owner_id
        organization = await db.organizations.find_one({"owner_id": current_user["_id"]})
        if not organization:
            raise HTTPException(
                status_code=404,
                detail="No organization found. Please complete onboarding."
            )

        # Update organization
        update_data = {
            "name": org_data.get("name"),
            "industry": org_data.get("industry"),
            "business_type": org_data.get("business_type"),
            "size": org_data.get("size"),
            "website": org_data.get("website"),
            "phone": org_data.get("phone"),
            "address": org_data.get("address"),
            "description": org_data.get("description"),
            "socials": org_data.get("socials"),
            "updated_at": datetime.utcnow()
        }

        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}

        result = await db.organizations.update_one(
            {"owner_id": current_user["_id"]},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Organization not found")

        return {"message": "Organization updated successfully"}

    except Exception as e:
        print(f"Error updating organization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 