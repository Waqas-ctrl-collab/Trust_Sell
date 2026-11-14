from typing import Optional
from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    id: str = Field(..., alias="_id")
    slug: str
    name: str
    description: str
    icon: str
    image_url: Optional[str] = None
    listing_count: int = 0
    sort_order: int = 0

    class Config:
        populate_by_name = True
