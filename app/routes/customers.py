from fastapi import APIRouter, Depends, Request, HTTPException
from ..models.customer import Customer, CustomerBase
from ..utils.auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[Customer])
async def get_customers(current_user: dict = Depends(get_current_user)):
    # Add customers retrieval logic here
    return [] 

@router.post("/", response_model=Customer)
async def create_customer(
    customer_data: CustomerBase,
    request: Request
):
    try:
        # Create customer with all required fields
        customer = {
            "organization_id": customer_data.organization_id,
            "name": customer_data.name,
            "email": customer_data.email,
            "phone": customer_data.phone,
            "channels": customer_data.channels or [],
            "tags": customer_data.tags or [],
            "last_contact": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await db.customers.insert_one(customer)
        created_customer = await db.customers.find_one({"_id": result.inserted_id})
        if created_customer:
            created_customer["id"] = str(created_customer["_id"])
            del created_customer["_id"]
        return created_customer

    except Exception as e:
        print(f"Create customer error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 