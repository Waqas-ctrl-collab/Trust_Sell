import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from app.config.db import get_collection
from app.models.listing import ListingDB
from app.schemas.listing import ListingResponse, ListingUpdate
from app.services.security import get_current_active_user
from app.services.verification import validate_and_save_upload, normalize_phone
from bson import ObjectId
from pymongo import ReturnDocument

logger = logging.getLogger("trust_sell.listings")
router = APIRouter(prefix="/listings", tags=["Listings"])

@router.post("/", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    title: str = Form(..., min_length=3, max_length=100),
    price: float = Form(..., gt=0),
    description: str = Form(..., min_length=10),
    category: str = Form(..., min_length=2, max_length=50),
    location: str = Form(..., min_length=2, max_length=100),
    seller_phone: str = Form(..., pattern=r"^\+?[0-9]{10,15}$"),
    images: List[UploadFile] = File(default=[]),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new marketplace listing (ad).
    Requires active user authentication. Supports multiple secure image uploads.
    """
    listings_collection = get_collection("listings")
    
    # 1. Loop and save images securely using the verification helper
    saved_images = []
    for file in images:
        # Ignore empty uploads that might occur in form submissions
        if file.filename:
            try:
                relative_path = validate_and_save_upload(
                    upload_file=file,
                    file_type="selfie",  # Uses image validation constraints (jpg, jpeg, png)
                    sub_folder="listings"
                )
                saved_images.append(relative_path)
            except Exception as e:
                logger.error(f"Failed to verify/save listing image upload: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to process image '{file.filename}': {str(e)}"
                )

    # 2. Map and serialize database payload
    listing_data = ListingDB(
        title=title.strip(),
        price=price,
        description=description.strip(),
        category=category.strip(),
        location=location.strip(),
        seller_id=current_user["_id"],
        seller_name=current_user["name"],
        seller_phone=normalize_phone(seller_phone),
        images=saved_images,
        status="active"
    )

    try:
        inserted = await listings_collection.insert_one(listing_data.to_dict())
        created_listing = await listings_collection.find_one({"_id": inserted.inserted_id})
        created_listing["_id"] = str(created_listing["_id"])
        
        logger.info(f"User {current_user['email']} successfully posted new listing: {title}")
        return created_listing
        
    except Exception as e:
        logger.error(f"Error inserting listing to database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit your listing. Please try again."
        )


@router.get("/", response_model=List[ListingResponse])
async def get_listings(
    category: Optional[str] = None,
    location: Optional[str] = None,
    q: Optional[str] = None,
    ad_status: Optional[str] = "active",
    limit: int = 50,
    skip: int = 0
):
    """
    Retrieve listings with pagination and filters.
    Can filter by category, location, ad_status, and query term 'q' (search in title or description).
    """
    listings_collection = get_collection("listings")
    query = {}

    if category:
        query["category"] = category
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}}
        ]
    if ad_status:
        query["status"] = ad_status

    try:
        cursor = (
            listings_collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        results = await cursor.to_list(length=limit)

        # Cast ObjectId values to string for serialization matching schemas
        for listing in results:
            listing["_id"] = str(listing["_id"])

        return results
    except Exception as e:
        logger.error(f"Failed to retrieve listings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving listings from database."
        )


@router.get("/user/me", response_model=List[ListingResponse])
async def get_my_listings(current_user: dict = Depends(get_current_active_user)):
    """
    Retrieve all listings owned by the currently authenticated user.
    Used for dashboard listing management ('My Ads').
    """
    listings_collection = get_collection("listings")
    
    try:
        cursor = listings_collection.find({"seller_id": current_user["_id"]}).sort("created_at", -1)
        results = await cursor.to_list(length=100)
        
        for listing in results:
            listing["_id"] = str(listing["_id"])
            
        return results
    except Exception as e:
        logger.error(f"Error fetching user's listings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user ads."
        )


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing_detail(listing_id: str):
    """
    Retrieve full details of a specific listing.
    Atomically increments the view count.
    """
    if not ObjectId.is_valid(listing_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid listing ID format."
        )

    listings_collection = get_collection("listings")
    
    try:
        # Atomically increment views counter and fetch modified document
        listing = await listings_collection.find_one_and_update(
            {"_id": ObjectId(listing_id)},
            {"$inc": {"views": 1}},
            return_document=ReturnDocument.AFTER
        )
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found or has been removed."
            )
            
        listing["_id"] = str(listing["_id"])
        return listing
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error loading listing {listing_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve listing details."
        )


@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: str,
    update_data: ListingUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update listing parameters.
    Requires that the authenticated user owns the listing, or holds an administrator role.
    """
    if not ObjectId.is_valid(listing_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid listing ID format."
        )

    listings_collection = get_collection("listings")
    
    # 1. Fetch listing to verify ownership
    listing = await listings_collection.find_one({"_id": ObjectId(listing_id)})
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found."
        )

    # 2. Security access control check
    if listing["seller_id"] != current_user["_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You do not own this listing."
        )

    # 3. Clean and map updates
    update_dict = {
        k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None
    }
    
    if update_dict:
        update_dict["updated_at"] = datetime.utcnow()
        try:
            await listings_collection.update_one(
                {"_id": ObjectId(listing_id)},
                {"$set": update_dict}
            )
            # Re-fetch latest document
            listing = await listings_collection.find_one({"_id": ObjectId(listing_id)})
            logger.info(f"Listing {listing_id} updated successfully by user {current_user['email']}")
        except Exception as e:
            logger.error(f"Failed to update listing in database: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update listing."
            )

    listing["_id"] = str(listing["_id"])
    return listing


@router.delete("/{listing_id}", status_code=status.HTTP_200_OK)
async def delete_listing(
    listing_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Permanently delete a listing.
    Requires that the authenticated user owns the listing, or holds an administrator role.
    """
    if not ObjectId.is_valid(listing_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid listing ID format."
        )

    listings_collection = get_collection("listings")
    
    # 1. Fetch listing to check ownership
    listing = await listings_collection.find_one({"_id": ObjectId(listing_id)})
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found."
        )

    # 2. Security validation
    if listing["seller_id"] != current_user["_id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You do not have permission to delete this listing."
        )

    try:
        await listings_collection.delete_one({"_id": ObjectId(listing_id)})
        logger.info(f"Listing {listing_id} deleted successfully by {current_user['email']}")
        return {"detail": "Listing successfully deleted."}
    except Exception as e:
        logger.error(f"Failed to delete listing {listing_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete listing."
        )
