from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl

class BrandDB(BaseModel):
    """
    Extensive identity and verification details for Brands.
    A Brand record links to a base User record.
    """
    user_id: str  # References UserDB ID as a string
    brand_name: str = Field(..., min_length=2, max_length=50)
    brand_category: str = Field(..., min_length=3, max_length=50)
    
    # Official Trademark / Registration details
    trademark_number: str = Field(..., min_length=4, max_length=50)
    certificate_url: str  # Path to verified PDF/Image of Trademark Certificate
    official_website: Optional[str] = None
    
    # Verification tracking
    verification_status: str = Field("pending", pattern="^(pending|approved|rejected)$")
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None  # Admin User ID
    rejection_reason: Optional[str] = None
    
    # Audit trail
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self):
        """Helper to serialize model values into pure MongoDB dicts."""
        return {
            "user_id": self.user_id,
            "brand_name": self.brand_name,
            "brand_category": self.brand_category,
            "trademark_number": self.trademark_number,
            "certificate_url": self.certificate_url,
            "official_website": self.official_website,
            "verification_status": self.verification_status,
            "verified_at": self.verified_at,
            "verified_by": self.verified_by,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
