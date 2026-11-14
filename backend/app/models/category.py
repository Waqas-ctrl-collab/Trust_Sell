from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CategoryDB(BaseModel):
    slug: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=80)
    description: str = Field(default="")
    icon: str = Field(default="fa-tag")
    image_url: Optional[str] = None
    listing_count: int = 0
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "image_url": self.image_url,
            "listing_count": self.listing_count,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }
