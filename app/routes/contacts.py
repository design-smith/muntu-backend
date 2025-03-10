from fastapi import APIRouter, Depends, HTTPException
from ..models.contact import Contact, ContactCreate
from ..utils.auth import get_current_user
from ..database import db
from datetime import datetime
from bson import ObjectId
from typing import List

router = APIRouter()

@router.post("/", response_model=Contact)
async def create_contact(
    contact_data: ContactCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        print(f"Received contact data: {contact_data}")
        
        # Create contact document
        contact_dict = {
            "name": contact_data.name,
            "email": contact_data.email,
            "phone": contact_data.phone,
            "company": contact_data.company,
            "notes": contact_data.notes,
            "organization_id": contact_data.organization_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",
            "type": "lead"
        }
        
        print(f"Prepared contact document: {contact_dict}")
        
        # Insert contact
        result = await db.contacts.insert_one(contact_dict)
        print(f"Insert result: {result.inserted_id}")
        
        # Get the created contact
        created_contact = await db.contacts.find_one({"_id": result.inserted_id})
        if created_contact:
            created_contact["id"] = str(created_contact["_id"])
            del created_contact["_id"]
            print(f"Created contact: {created_contact}")
            return Contact(**created_contact)
        
        raise HTTPException(status_code=404, detail="Contact not found after creation")
        
    except Exception as e:
        error_msg = f"Error creating contact: {str(e)}"
        print(error_msg)
        if hasattr(e, '__dict__'):
            print(f"Error details: {e.__dict__}")
        raise HTTPException(
            status_code=422,
            detail=error_msg
        )

@router.get("/")
async def get_contacts(current_user: dict = Depends(get_current_user)):
    try:
        # Check if user has an organization
        if not current_user.get("organization_id"):
            return {
                "contacts": [],
                "message": "Please complete organization setup in onboarding"
            }

        # Fetch contacts for the organization
        contacts = await db.contacts.find({
            "organization_id": current_user["organization_id"]
        }).to_list(None)

        # Format contacts for response
        formatted_contacts = [
            {
                "id": str(contact["_id"]),
                "name": contact.get("name", ""),
                "email": contact.get("email", ""),
                "phone": contact.get("phone", ""),
                "company": contact.get("company", ""),
                "notes": contact.get("notes", ""),
                "status": contact.get("status", "active"),
                "created_at": contact.get("created_at", datetime.utcnow()),
                "updated_at": contact.get("updated_at", datetime.utcnow())
            }
            for contact in contacts
        ]

        return {"contacts": formatted_contacts}

    except Exception as e:
        print(f"Error fetching contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 