from fastapi import APIRouter, Depends, HTTPException, Request
from ..models.product import Product, ProductCreate
from ..utils.auth import get_current_user
from ..database import db
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=list[Product])
async def get_products(current_user: dict = Depends(get_current_user)):
    # Add products retrieval logic here
    return []

@router.post("/", response_model=Product)
async def create_product(
    product_data: ProductCreate,
    request: Request
):
    try:
        # Create product with all required fields
        product = {
            "name": product_data.name,
            "category": product_data.category,
            "short_description": product_data.short_description,
            "long_description": product_data.long_description,
            "price_type": product_data.price_type,
            "price": product_data.price,
            "price_min": product_data.price_min,
            "price_max": product_data.price_max,
            "price_unit": product_data.price_unit,
            "organization_id": product_data.organization_id,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Insert into database
        result = await db.products.insert_one(product)
        
        # Get the created product
        created_product = await db.products.find_one({"_id": result.inserted_id})
        if created_product:
            # Convert _id to string id
            created_product["id"] = str(created_product["_id"])
            del created_product["_id"]

        return created_product

    except Exception as e:
        print(f"Create product error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 