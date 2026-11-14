import logging
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from app.config.db import get_collection
from app.config.settings import settings, BASE_DIR
from app.models.user import UserDB
from app.models.seller import SellerDB
from app.models.brand import BrandDB
from app.schemas.user import UserResponse
from app.services.security import get_password_hash
from app.services.verification import validate_and_save_upload, normalize_phone
from app.services.otp_service import consume_otp_token
from app.services.ai_verification import verify_identity_documents
from bson import ObjectId

logger = logging.getLogger("trust_sell.secure_signup")
router = APIRouter(prefix="/auth/signup", tags=["Secure Signup"])


@router.post("/secure", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def secure_signup(
    name: str = Form(..., min_length=3, max_length=50),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(..., min_length=8),
    role: str = Form(..., pattern="^(buyer|seller|brand)$"),
    cnic_number: str = Form(..., pattern=r"^[0-9]{5}-[0-9]{7}-[0-9]{1}$"),
    otp_token: str = Form(...),
    city: Optional[str] = Form(None),
    selfie: UploadFile = File(...),
    cnic_image: UploadFile = File(...),
    shop_name: Optional[str] = Form(None),
    seller_category: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
    brand_name: Optional[str] = Form(None),
    brand_category: Optional[str] = Form(None),
    trademark_number: Optional[str] = Form(None),
    certificate: Optional[UploadFile] = File(None),
):
    """
  eBay-grade secure onboarding: OTP + live selfie + CNIC + AI biometric/CNIC audit.
    """
    users_collection = get_collection("users")
    normalized_email = email.strip().lower()
    normalized_phone = normalize_phone(phone)

    if not consume_otp_token(otp_token, normalized_phone):
        raise HTTPException(status_code=400, detail="Invalid or expired phone verification. Verify OTP again.")

    if await users_collection.find_one({"email": normalized_email}):
        raise HTTPException(status_code=400, detail="Email already registered.")
    if await users_collection.find_one({"phone": normalized_phone}):
        raise HTTPException(status_code=400, detail="Phone already registered.")

    sub = role + "s" if role != "brand" else "brands"
    selfie_path = validate_and_save_upload(selfie, "selfie", sub)
    cnic_path = validate_and_save_upload(cnic_image, "document", sub)

    audit = verify_identity_documents(
        selfie_path, cnic_path, cnic_number, BASE_DIR
    )
    if not audit.overall_verified:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Identity verification failed.",
                "reasons": audit.rejection_reasons,
                "biometric_score": audit.biometric_match_score,
            },
        )

    verification_status = "verified" if role == "buyer" else "pending"
    user_data = UserDB(
        name=name.strip(),
        email=normalized_email,
        phone=normalized_phone,
        hashed_password=get_password_hash(password),
        role=role,
        selfie_url=selfie_path,
        cnic_url=cnic_path,
        cnic_number=cnic_number.strip(),
        city=city.strip() if city else None,
        phone_verified=True,
        verification_status=verification_status,
        biometric_match_score=audit.biometric_match_score,
        cnic_verified=audit.cnic_database_match,
        security_audit_id=audit.audit_id,
    )

    try:
        inserted = await users_collection.insert_one(user_data.to_dict())
        user_id_str = str(inserted.inserted_id)

        if role == "seller":
            if not shop_name or not seller_category:
                await users_collection.delete_one({"_id": inserted.inserted_id})
                raise HTTPException(status_code=400, detail="Shop name and seller category required.")
            sellers_col = get_collection("sellers")
            doc_path = None
            if document and document.filename:
                doc_path = validate_and_save_upload(document, "document", "sellers")
            await sellers_col.insert_one(
                SellerDB(
                    user_id=user_id_str,
                    shop_name=shop_name.strip(),
                    seller_category=seller_category,
                    cnic_number=cnic_number.strip(),
                    document_url=doc_path or cnic_path,
                    verification_status="pending",
                ).to_dict()
            )

        elif role == "brand":
            if not brand_name or not trademark_number:
                await users_collection.delete_one({"_id": inserted.inserted_id})
                raise HTTPException(status_code=400, detail="Brand name and trademark number required.")
            if not certificate or not certificate.filename:
                await users_collection.delete_one({"_id": inserted.inserted_id})
                raise HTTPException(status_code=400, detail="Trademark certificate required for brands.")
            brands_col = get_collection("brands")
            cert_path = validate_and_save_upload(certificate, "document", "brands")
            await brands_col.insert_one(
                BrandDB(
                    user_id=user_id_str,
                    brand_name=brand_name.strip(),
                    brand_category=(brand_category or "General").strip(),
                    trademark_number=trademark_number.strip(),
                    certificate_url=cert_path,
                    verification_status="pending",
                ).to_dict()
            )

        created = await users_collection.find_one({"_id": inserted.inserted_id})
        created["_id"] = user_id_str
        logger.info(f"Secure signup complete: {normalized_email} role={role} audit={audit.audit_id}")
        return created

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Secure signup failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")
