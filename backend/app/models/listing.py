from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ListingDB(BaseModel):
    """
    Core Listing database schema representation.
    Represents product ads in the MongoDB database.
    """
    title: str = Field(..., min_length=3, max_length=100)
    price: float = Field(..., gt=0)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=2, max_length=50)
    location: str = Field(..., min_length=2, max_length=100)
    
    # Seller information (links to base User record)
    seller_id: str  # References User ObjectId as a string
    seller_name: str
    seller_phone: str
    
    # Ad status and media
    status: str = Field("active", pattern="^(active|sold|inactive)$")
    images: List[str] = Field(default_factory=list)  # Paths to verified listing image uploads
    views: int = Field(default=0)
    
    # Audit trail metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self):
        """Helper to serialize model values into pure MongoDB dicts."""
        return {
            "title": self.title,
            "price": self.price,
            "description": self.description,
            "category": self.category,
            "location": self.location,
            "seller_id": self.seller_id,
            "seller_name": self.seller_name,
            "seller_phone": self.seller_phone,
            "status": self.status,
            "images": self.images,
            "views": self.views,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
