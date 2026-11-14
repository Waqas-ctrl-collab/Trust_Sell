import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.config.db import get_collection
from app.schemas.brand import BrandResponse
from app.schemas.user import UserResponse
from app.services.security import get_current_active_user, RequireRole
from bson import ObjectId

logger = logging.getLogger("trust_sell.brands")
router = APIRouter(prefix="/brands", tags=["Brands"])

async def _build_brand_response(brand_doc: dict) -> dict:
    """Helper to populate nested representative user details for a brand record."""
    brand_doc["_id"] = str(brand_doc["_id"])
    user_id = brand_doc.get("user_id")
    
    users_collection = get_collection("users")
    user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if user_doc:
        user_doc["_id"] = str(user_doc["_id"])
        brand_doc["user"] = user_doc
    return brand_doc

@router.get("/me", response_model=BrandResponse)
async def get_my_brand_profile(current_user: dict = Depends(RequireRole(["brand"]))):
    """
    Retrieve trademark and registration profile for currently logged-in brand owner.
    """
    brands_collection = get_collection("brands")
    brand = await brands_collection.find_one({"user_id": current_user["id"]})
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found for this account."
        )
        
    return await _build_brand_response(brand)


@router.get("/pending", response_model=List[BrandResponse])
async def list_pending_brands(admin_user: dict = Depends(RequireRole(["admin"]))):
    """
    Admin Only: List all brands awaiting trademark validation.
    """
    brands_collection = get_collection("brands")
    cursor = brands_collection.find({"verification_status": "pending"})
    
    pending_brands = []
    async for brand in cursor:
        populated = await _build_brand_response(brand)
        pending_brands.append(populated)
        
    return pending_brands


@router.post("/{brand_id}/verify", response_model=BrandResponse)
async def verify_brand(
    brand_id: str,
    approve: bool,
    rejection_reason: str = None,
    admin_user: dict = Depends(RequireRole(["admin"]))
):
    """
    Admin Only: Approve or Reject a brand's trademark application and profile.
    """
    brands_collection = get_collection("brands")
    
    if not ObjectId.is_valid(brand_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid brand ID format."
        )

    brand = await brands_collection.find_one({"_id": ObjectId(brand_id)})
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found."
        )

    # Transition verification status
    status_value = "approved" if approve else "rejected"
    update_data = {
        "verification_status": status_value,
        "verified_at": datetime.utcnow() if approve else None,
        "verified_by": admin_user["id"],
        "rejection_reason": rejection_reason if not approve else None,
        "updated_at": datetime.utcnow()
    }

    try:
        await brands_collection.update_one(
            {"_id": ObjectId(brand_id)},
            {"$set": update_data}
        )
        
        # Load updated record
        updated_brand = await brands_collection.find_one({"_id": ObjectId(brand_id)})
        logger.info(f"Admin {admin_user.get('email')} updated brand {brand_id} status to {status_value}")
        return await _build_brand_response(updated_brand)
        
    except Exception as e:
        logger.error(f"Failed to update brand verification status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing brand verification status change."
        )
