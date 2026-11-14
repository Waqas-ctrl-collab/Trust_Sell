from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse

class BrandResponse(BaseModel):
    """
    View representation for Brand information.
    Embedded with representative user profile.
    """
    id: str = Field(..., alias="_id")
    user_id: str
    brand_name: str
    brand_category: str
    trademark_number: str
    certificate_url: str
    official_website: Optional[str] = None
    verification_status: str
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Embedded owner user details
    user: Optional[UserResponse] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
