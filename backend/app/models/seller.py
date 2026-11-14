from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class SellerDB(BaseModel):
    """
    Extensive identity and verification details for Sellers.
    A Seller record links to a base User record.
    """
    user_id: str  # References UserDB ID as a string
    shop_name: str = Field(..., min_length=3, max_length=50)
    seller_category: str = Field(..., pattern="^(Individual|Retailer|Wholesaler|Manufacturer)$")
    
    # Official Identity details
    cnic_number: str = Field(..., pattern=r"^[0-9]{5}-[0-9]{7}-[0-9]{1}$")  # Standard CNIC format (13 digits with hyphens)
    business_registration_number: Optional[str] = None
    
    # Document storage link
    document_url: str  # Path to verified PDF/Image of CNIC/Trade license
    
    # Verification and Trust tracking
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
            "shop_name": self.shop_name,
            "seller_category": self.seller_category,
            "cnic_number": self.cnic_number,
            "business_registration_number": self.business_registration_number,
            "document_url": self.document_url,
            "verification_status": self.verification_status,
            "verified_at": self.verified_at,
            "verified_by": self.verified_by,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
