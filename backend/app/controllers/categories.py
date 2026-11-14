import logging
from typing import List
from fastapi import APIRouter, HTTPException
from app.config.db import get_collection
from app.schemas.category import CategoryResponse

logger = logging.getLogger("trust_sell.categories")
router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
async def list_categories():
    """All active marketplace categories with live listing counts."""
    categories_col = get_collection("categories")
    listings_col = get_collection("listings")

    cursor = categories_col.find({"is_active": True}).sort("sort_order", 1)
    categories = await cursor.to_list(length=50)

    for cat in categories:
        count = await listings_col.count_documents(
            {"category": cat["slug"], "status": "active"}
        )
        cat["listing_count"] = count
        cat["_id"] = str(cat["_id"])

    return categories


@router.get("/{slug}", response_model=CategoryResponse)
async def get_category(slug: str):
    categories_col = get_collection("categories")
    listings_col = get_collection("listings")

    cat = await categories_col.find_one({"slug": slug, "is_active": True})
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")

    cat["listing_count"] = await listings_col.count_documents(
        {"category": slug, "status": "active"}
    )
    cat["_id"] = str(cat["_id"])
    return cat
