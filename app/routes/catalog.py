from fastapi import APIRouter, Depends, Request
from ..models.catalog import CatalogItem, CatalogItemBase
from ..utils.auth import get_current_user
from datetime import datetime
from fastapi import HTTPException

router = APIRouter()

@router.get("/", response_model=list[CatalogItem])
async def get_catalog_items(current_user: dict = Depends(get_current_user)):
    # Add catalog items retrieval logic here
    return []

@router.post("/", response_model=CatalogItem)
async def create_catalog_item(
    item_data: CatalogItemBase,
    request: Request
):
    try:
        # Create catalog item with all required fields
        catalog_item = {
            "organization_id": item_data.organization_id,
            "name": item_data.name,
            "type": item_data.type,
            "description": {
                "short": item_data.description.get("short", ""),
                "long": item_data.description.get("long", "")
            },
            "pricing": {
                "type": item_data.pricing.get("type", "fixed"),
                "value": item_data.pricing.get("value"),
                "min": item_data.pricing.get("min"),
                "max": item_data.pricing.get("max"),
                "unit": item_data.pricing.get("unit")
            },
            "metadata": {
                "tags": item_data.metadata.get("tags", []),
                "category": item_data.metadata.get("category", ""),
                "custom_fields": item_data.metadata.get("custom_fields", {})
            },
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await db.catalog.insert_one(catalog_item)
        created_item = await db.catalog.find_one({"_id": result.inserted_id})
        if created_item:
            created_item["id"] = str(created_item["_id"])
            del created_item["_id"]
        return created_item

    except Exception as e:
        print(f"Create catalog item error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 