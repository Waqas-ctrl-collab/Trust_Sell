from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse

class SellerResponse(BaseModel):
    """
    View representation for Seller information.
    Embedded with standard user profile elements.
    """
    id: str = Field(..., alias="_id")
    user_id: str
    shop_name: str
    seller_category: str
    cnic_number: str
    business_registration_number: Optional[str] = None
    document_url: str
    verification_status: str
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Embedded user details for a unified presentation
    user: Optional[UserResponse] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
