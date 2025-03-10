from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    category: str  # 'product' | 'service'
    short_description: str
    long_description: Optional[str] = None
    price_type: str  # 'fixed' | 'hourly' | 'range' | 'quote'
    price: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    price_unit: Optional[str] = None
    organization_id: str
    status: str = "active"

class Product(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime

class ProductCreate(BaseModel):
    name: str
    category: str
    short_description: str
    long_description: Optional[str] = None
    price_type: str
    price: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    price_unit: Optional[str] = None
    organization_id: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price_type: Optional[str] = None
    price: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    price_unit: Optional[str] = None 