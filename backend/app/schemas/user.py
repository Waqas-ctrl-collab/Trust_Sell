from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserResponse(BaseModel):
    """
    View presentation layer for a User profile.
    Explicitly filters out the hashed password and private database fields.
    """
    id: str = Field(..., alias="_id")  # Map from MongoDB _id
    name: str
    email: EmailStr
    phone: str
    role: str
    is_active: bool
    selfie_url: Optional[str] = None
    cnic_verified: bool = False
    phone_verified: bool = False
    verification_status: str = "pending"
    biometric_match_score: float = 0.0
    city: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True  # Allows parsing dictionary containing either '_id' or 'id'
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9b1d8b2a3c8e4d56",
                "name": "Jane Doe",
                "email": "janedoe@example.com",
                "phone": "+923009876543",
                "role": "buyer",
                "is_active": True,
                "selfie_url": "uploads/buyers/selfie/abc123xyz.png",
                "created_at": "2026-05-28T23:25:00Z",
                "updated_at": "2026-05-28T23:25:00Z"
            }
        }
class UserSelfieUpdate(BaseModel):
    """View schema for updating user selfie."""
    selfie_url: str
