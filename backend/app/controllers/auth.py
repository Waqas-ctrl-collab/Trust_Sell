import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response
from app.config.db import get_collection
from app.models.user import UserDB
from app.models.seller import SellerDB
from app.models.brand import BrandDB
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.config.settings import settings
from app.services.security import get_password_hash, verify_password, create_access_token
from app.services.verification import validate_and_save_upload, normalize_phone
from bson import ObjectId

logger = logging.getLogger("trust_sell.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup/buyer", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup_buyer(
    name: str = Form(..., min_length=3, max_length=50),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(..., min_length=8),
    selfie: UploadFile = File(...) # Mandated secure selfie upload for identity verification
):
    """
    Register a standard Buyer with verified email, phone, and camera face verification upload.
    """
    users_collection = get_collection("users")
    
    # 1. Deduplicate check
    normalized_email = email.strip().lower()
    if await users_collection.find_one({"email": normalized_email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered."
        )
        
    normalized_phone = normalize_phone(phone)
    if await users_collection.find_one({"phone": normalized_phone}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this phone number is already registered."
        )

    # 2. Securely store face photo
    selfie_path = validate_and_save_upload(
        upload_file=selfie,
        file_type="selfie",
        sub_folder="buyers"
    )

    # 3. Create database entry
    hashed_pwd = get_password_hash(password)
    user_data = UserDB(
        name=name.strip(),
        email=normalized_email,
        phone=normalized_phone,
        hashed_password=hashed_pwd,
        role="buyer",
        selfie_url=selfie_path
    )

    try:
        inserted = await users_collection.insert_one(user_data.to_dict())
        created_user = await users_collection.find_one({"_id": inserted.inserted_id})
        created_user["_id"] = str(created_user["_id"])
        
        logger.info(f"Successfully registered buyer user: {normalized_email}")
        return created_user
        
    except Exception as e:
        logger.error(f"Error occurred during buyer database insertion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user. Please try again later."
        )


@router.post("/signup/seller", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup_seller(
    name: str = Form(..., min_length=3, max_length=50),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(..., min_length=8),
    shop_name: str = Form(..., min_length=3, max_length=50),
    seller_category: str = Form(..., pattern="^(Individual|Retailer|Wholesaler|Manufacturer)$"),
    cnic_number: str = Form(..., pattern=r"^[0-9]{5}-[0-9]{7}-[0-9]{1}$"),
    business_registration_number: str = Form(None),
    selfie: UploadFile = File(...),      # Mandatory face image
    document: UploadFile = File(...)      # Mandatory National Identity document (CNIC/Trade License)
):
    """
    Onboard a Seller.
    Requires Name, Email, Password, Shop info, CNIC (ID Card), trade documents, and a Live selfie.
    Initially defaults to 'pending' status, requiring Admin approval.
    """
    users_collection = get_collection("users")
    sellers_collection = get_collection("sellers")

    # 1. Deduplicate check
    normalized_email = email.strip().lower()
    if await users_collection.find_one({"email": normalized_email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered."
        )
        
    normalized_phone = normalize_phone(phone)
    if await users_collection.find_one({"phone": normalized_phone}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this phone number is already registered."
        )

    if await sellers_collection.find_one({"shop_name": shop_name.strip()}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A shop with this name already exists. Please choose a unique shop name."
        )

    if await sellers_collection.find_one({"cnic_number": cnic_number.strip()}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A seller with this CNIC/National ID is already registered."
        )

    # 2. Upload verification documents securely
    selfie_path = validate_and_save_upload(
        upload_file=selfie,
        file_type="selfie",
        sub_folder="sellers"
    )
    document_path = validate_and_save_upload(
        upload_file=document,
        file_type="document",
        sub_folder="sellers"
    )

    # 3. Save Base User (role="seller")
    hashed_pwd = get_password_hash(password)
    user_data = UserDB(
        name=name.strip(),
        email=normalized_email,
        phone=normalized_phone,
        hashed_password=hashed_pwd,
        role="seller",
        selfie_url=selfie_path
    )

    try:
        user_inserted = await users_collection.insert_one(user_data.to_dict())
        user_id_str = str(user_inserted.inserted_id)

        # 4. Save Seller-specific registration
        seller_data = SellerDB(
            user_id=user_id_str,
            shop_name=shop_name.strip(),
            seller_category=seller_category,
            cnic_number=cnic_number.strip(),
            business_registration_number=business_registration_number.strip() if business_registration_number else None,
            document_url=document_path,
            verification_status="pending" # High Security: Defaults to pending approval
        )
        
        await sellers_collection.insert_one(seller_data.to_dict())

        created_user = await users_collection.find_one({"_id": ObjectId(user_id_str)})
        created_user["_id"] = user_id_str
        
        logger.info(f"Successfully registered pending seller: {normalized_email} for shop: {shop_name}")
        return created_user

    except Exception as e:
        logger.error(f"Error occurred during seller signup transaction: {str(e)}")
        # Rollback User record if Seller insertion fails to keep DB consistent
        if 'user_id_str' in locals():
            await users_collection.delete_one({"_id": ObjectId(user_id_str)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register seller profile. Please verify your data and try again."
        )


@router.post("/signup/brand", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup_brand(
    name: str = Form(..., min_length=3, max_length=50),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(..., min_length=8),
    brand_name: str = Form(..., min_length=2, max_length=50),
    brand_category: str = Form(..., min_length=3, max_length=50),
    trademark_number: str = Form(..., min_length=4, max_length=50),
    official_website: str = Form(None),
    selfie: UploadFile = File(...),         # Official representative selfie
    certificate: UploadFile = File(...)     # Official trademark certificate upload
):
    """
    Onboard a Brand Owner/Representative.
    Requires Trademark Verification, Trademark Registration Number, official documents, and Live Selfie.
    Initially defaults to 'pending' status, requiring admin validation.
    """
    users_collection = get_collection("users")
    brands_collection = get_collection("brands")

    # 1. Deduplicate check
    normalized_email = email.strip().lower()
    if await users_collection.find_one({"email": normalized_email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered."
        )
        
    normalized_phone = normalize_phone(phone)
    if await users_collection.find_one({"phone": normalized_phone}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this phone number is already registered."
        )

    if await brands_collection.find_one({"brand_name": brand_name.strip()}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A brand with this name is already registered."
        )

    if await brands_collection.find_one({"trademark_number": trademark_number.strip()}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A brand with this trademark registration number already exists."
        )

    # 2. Upload verification documents securely
    selfie_path = validate_and_save_upload(
        upload_file=selfie,
        file_type="selfie",
        sub_folder="brands"
    )
    certificate_path = validate_and_save_upload(
        upload_file=certificate,
        file_type="document",
        sub_folder="brands"
    )

    # 3. Save Base User (role="brand")
    hashed_pwd = get_password_hash(password)
    user_data = UserDB(
        name=name.strip(),
        email=normalized_email,
        phone=normalized_phone,
        hashed_password=hashed_pwd,
        role="brand",
        selfie_url=selfie_path
    )

    try:
        user_inserted = await users_collection.insert_one(user_data.to_dict())
        user_id_str = str(user_inserted.inserted_id)

        # 4. Save Brand-specific registration
        brand_data = BrandDB(
            user_id=user_id_str,
            brand_name=brand_name.strip(),
            brand_category=brand_category.strip(),
            trademark_number=trademark_number.strip(),
            certificate_url=certificate_path,
            official_website=official_website.strip() if official_website else None,
            verification_status="pending" # High Security: Defaults to pending approval
        )
        
        await brands_collection.insert_one(brand_data.to_dict())

        created_user = await users_collection.find_one({"_id": ObjectId(user_id_str)})
        created_user["_id"] = user_id_str
        
        logger.info(f"Successfully registered pending brand: {normalized_email} for brand: {brand_name}")
        return created_user

    except Exception as e:
        logger.error(f"Error occurred during brand signup transaction: {str(e)}")
        # Rollback User record if Brand insertion fails
        if 'user_id_str' in locals():
            await users_collection.delete_one({"_id": ObjectId(user_id_str)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register brand profile. Please check your data."
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    response: Response
):
    """
    Authenticate user. Issues a secure JWT access token.
    Stores the token in a secure, HttpOnly, SameSite cookie AND returns it in JSON payload.
    """
    users_collection = get_collection("users")
    email_search = credentials.email.strip().lower()
    
    user = await users_collection.find_one({"email": email_search})
    if not user:
        # Avoid telling the attacker if the email was right or wrong (Generic message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email address or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify password hash
    if not verify_password(credentials.password, user.get("hashed_password")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email address or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check if account is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )

    # Build access token claims
    user_id_str = str(user["_id"])
    token_claims = {
        "sub": user_id_str,
        "role": user.get("role", "buyer"),
        "email": user.get("email")
    }
    
    access_token = create_access_token(data=token_claims)

    # Security: Set cookie with HttpOnly, Secure, and SameSite parameters
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=settings.COOKIE_SECURE,  # True in production (HTTPS)
        samesite="lax",       # Prevents CSRF attacks
        max_age=120 * 60,     # Matches expiration (120 minutes)
    )

    user["_id"] = user_id_str
    
    logger.info(f"User login successful: {email_search} (Role: {user.get('role')})")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/logout")
async def logout(response: Response):
    """Logs the user out by clearing the secure HttpOnly session cookie."""
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out and cleared session."}
