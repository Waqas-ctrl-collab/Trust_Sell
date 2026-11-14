import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.config.db import get_collection
from app.schemas.user import UserResponse
from app.services.security import get_current_active_user
from app.services.verification import validate_and_save_upload
from bson import ObjectId

logger = logging.getLogger("trust_sell.users")
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: dict = Depends(get_current_active_user)):
    """
    Retrieve the current logged-in user's profile.
    Requires active session token.
    """
    return current_user


@router.post("/me/selfie", response_model=UserResponse)
async def update_my_selfie(
    selfie: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update/upload a new live camera picture (selfie) for identity verification.
    """
    users_collection = get_collection("users")
    
    # 1. Determine sub_folder category based on user role
    role = current_user.get("role", "buyer")
    sub_folder = "buyers" if role == "buyer" else ("sellers" if role == "seller" else "brands")

    # 2. Securely validate and save image file
    selfie_path = validate_and_save_upload(
        upload_file=selfie,
        file_type="selfie",
        sub_folder=sub_folder
    )

    # 3. Update in database
    user_id = current_user["id"] # Clean string id passed by dependency
    try:
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"selfie_url": selfie_path}}
        )
        
        # Reload updated user profile
        updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        updated_user["_id"] = str(updated_user["_id"])
        
        logger.info(f"Selfie image updated successfully for user: {current_user.get('email')}")
        return updated_user
        
    except Exception as e:
        logger.error(f"Failed to update selfie path in database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating identity profile image."
        )
