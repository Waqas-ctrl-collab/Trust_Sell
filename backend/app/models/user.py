from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserDB(BaseModel):
    """
    Core User database schema representation.
    Used for buyers, sellers, brands, and admins in MongoDB.
    """
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")  # Validates standard E.164 phone formats
    hashed_password: str
    role: str = Field("buyer", pattern="^(buyer|seller|brand|admin)$")
    is_active: bool = True
    
    # Secure Verification elements
    selfie_url: Optional[str] = None
    cnic_url: Optional[str] = None
    cnic_number: Optional[str] = None
    city: Optional[str] = None
    phone_verified: bool = False
    verification_status: str = Field(
        default="pending",
        pattern="^(pending|verified|rejected|review)$",
    )
    biometric_match_score: float = 0.0
    cnic_verified: bool = False
    security_audit_id: Optional[str] = None

    # Audit trail metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "johndoe@example.com",
                "phone": "+923001234567",
                "role": "buyer",
                "is_active": True,
                "selfie_url": "uploads/buyers/selfie/abc123xyz.png",
                "created_at": "2026-05-28T23:25:00Z"
            }
        }

    def to_dict(self):
        """Helper to serialize model values into pure MongoDB dicts."""
        return {
            "name": self.name,
            "email": self.email.lower(),  # Always store lowercased email for security comparisons
            "phone": self.phone,
            "hashed_password": self.hashed_password,
            "role": self.role,
            "is_active": self.is_active,
            "selfie_url": self.selfie_url,
            "cnic_url": self.cnic_url,
            "cnic_number": self.cnic_number,
            "city": self.city,
            "phone_verified": self.phone_verified,
            "verification_status": self.verification_status,
            "biometric_match_score": self.biometric_match_score,
            "cnic_verified": self.cnic_verified,
            "security_audit_id": self.security_audit_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
