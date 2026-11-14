import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.config.db import get_collection
from app.schemas.seller import SellerResponse
from app.schemas.user import UserResponse
from app.services.security import get_current_active_user, RequireRole
from bson import ObjectId

logger = logging.getLogger("trust_sell.sellers")
router = APIRouter(prefix="/sellers", tags=["Sellers"])

async def _build_seller_response(seller_doc: dict) -> dict:
    """Helper to populate the nested user data in a seller document."""
    seller_doc["_id"] = str(seller_doc["_id"])
    user_id = seller_doc.get("user_id")
    
    users_collection = get_collection("users")
    user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if user_doc:
        user_doc["_id"] = str(user_doc["_id"])
        seller_doc["user"] = user_doc
    return seller_doc

@router.get("/me", response_model=SellerResponse)
async def get_my_seller_profile(current_user: dict = Depends(RequireRole(["seller"]))):
    """
    Get the seller verification profile and status for the currently logged-in seller.
    """
    sellers_collection = get_collection("sellers")
    seller = await sellers_collection.find_one({"user_id": current_user["id"]})
    
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller profile not found for this account."
        )
        
    return await _build_seller_response(seller)


@router.get("/pending", response_model=List[SellerResponse])
async def list_pending_sellers(admin_user: dict = Depends(RequireRole(["admin"]))):
    """
    Admin Only: List all sellers currently in 'pending' status awaiting identity validation.
    """
    sellers_collection = get_collection("sellers")
    cursor = sellers_collection.find({"verification_status": "pending"})
    
    pending_sellers = []
    async for seller in cursor:
        populated = await _build_seller_response(seller)
        pending_sellers.append(populated)
        
    return pending_sellers


@router.post("/{seller_id}/verify", response_model=SellerResponse)
async def verify_seller(
    seller_id: str,
    approve: bool,
    rejection_reason: str = None,
    admin_user: dict = Depends(RequireRole(["admin"]))
):
    """
    Admin Only: Approve or Reject a seller's identity and onboarding application.
    Updates the seller's trust status dynamically.
    """
    sellers_collection = get_collection("sellers")
    
    if not ObjectId.is_valid(seller_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid seller ID format."
        )

    seller = await sellers_collection.find_one({"_id": ObjectId(seller_id)})
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller profile not found."
        )

    # Calculate status update details
    status_value = "approved" if approve else "rejected"
    update_data = {
        "verification_status": status_value,
        "verified_at": datetime.utcnow() if approve else None,
        "verified_by": admin_user["id"],
        "rejection_reason": rejection_reason if not approve else None,
        "updated_at": datetime.utcnow()
    }

    try:
        await sellers_collection.update_one(
            {"_id": ObjectId(seller_id)},
            {"$set": update_data}
        )
        
        # Load updated record
        updated_seller = await sellers_collection.find_one({"_id": ObjectId(seller_id)})
        logger.info(f"Admin {admin_user.get('email')} updated seller {seller_id} status to {status_value}")
        return await _build_seller_response(updated_seller)
        
    except Exception as e:
        logger.error(f"Failed to update seller verification status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing seller verification status change."
        )
