from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ListingCreate(BaseModel):
    """View schema for creating a Listing."""
    title: str = Field(..., min_length=3, max_length=100)
    price: float = Field(..., gt=0)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=2, max_length=50)
    location: str = Field(..., min_length=2, max_length=100)
    seller_phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")

class ListingUpdate(BaseModel):
    """View schema for updating an existing Listing."""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|sold|inactive)$")
    seller_phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")

class ListingResponse(BaseModel):
    """View schema for serialized Listing details returned to the frontend."""
    id: str = Field(..., alias="_id")
    title: str
    price: float
    description: str
    category: str
    location: str
    seller_id: str
    seller_name: str
    seller_phone: str
    status: str
    images: List[str]
    views: int
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9b1d8b2a3c8e4d56",
                "title": "iPhone 12 Pro Max - 256GB - Excellent Condition",
                "price": 45000.0,
                "description": "iPhone 12 Pro Max in excellent condition. 256GB storage capacity. Battery health is 92%.",
                "category": "mobile",
                "location": "Lahore, Punjab",
                "seller_id": "60c72b2f9b1d8b2a3c8e4d55",
                "seller_name": "Ahmed Raza",
                "seller_phone": "+923001234567",
                "status": "active",
                "images": ["uploads/listings/abc123xyz.png"],
                "views": 124,
                "created_at": "2026-05-28T23:25:00Z",
                "updated_at": "2026-05-28T23:25:00Z"
            }
        }
