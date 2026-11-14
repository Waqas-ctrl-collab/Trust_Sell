import logging
import uuid
from pathlib import Path
from typing import List, Set
from fastapi import UploadFile, HTTPException, status
from app.config.settings import settings

logger = logging.getLogger("trust_sell.verification")

# Security File Constants
ALLOWED_IMAGE_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png"}
ALLOWED_DOCUMENT_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".pdf"}
ALLOWED_MIME_TYPES: Set[str] = {"image/jpeg", "image/png", "application/pdf"}

MAX_IMAGE_SIZE_BYTES = 3 * 1024 * 1024       # 3 Megabytes for selfies
MAX_DOCUMENT_SIZE_BYTES = 5 * 1024 * 1024    # 5 Megabytes for credentials/certifications


def normalize_phone(phone: str) -> str:
    """Strip spaces/dashes from phone numbers (e.g. 0300-1234567 -> 03001234567)."""
    cleaned = phone.strip()
    if cleaned.startswith("+"):
        return "+" + "".join(c for c in cleaned[1:] if c.isdigit())
    return "".join(c for c in cleaned if c.isdigit())

def validate_and_save_upload(
    upload_file: UploadFile,
    file_type: str,  # "selfie" or "document"
    sub_folder: str  # "buyers", "sellers", "brands"
) -> str:
    """
    Validates the uploaded file for:
    1. Maximum file size to prevent Denial of Service (DoS) attacks.
    2. File extension to prevent executable upload exploits.
    3. MIME Content-Type matching allowed lists.
    
    Then, it sanitizes and saves the file with a completely random UUID filename to prevent:
    - Path traversal attacks (e.g. filename like '../../app/main.py')
    - Filename collisons.
    
    Returns the relative web-accessible/storage path.
    """
    # 1. Determine constraints based on file type
    if file_type == "selfie":
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS
        max_size = MAX_IMAGE_SIZE_BYTES
        type_label = "Selfie image"
    elif file_type == "document":
        allowed_extensions = ALLOWED_DOCUMENT_EXTENSIONS
        max_size = MAX_DOCUMENT_SIZE_BYTES
        type_label = "Identity document"
    else:
        raise ValueError("Invalid file verification type specified.")

    # 2. Extract and sanitize extension
    original_path = Path(upload_file.filename)
    extension = original_path.suffix.lower()
    
    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension {extension}. Only {', '.join(allowed_extensions)} are allowed for {type_label}s."
        )

    # 3. Verify Content-Type Header
    if upload_file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Received: '{upload_file.content_type}'."
        )

    # 4. Perform Size Checking dynamically (without reading the entire file into memory at once)
    size = 0
    chunk_size = 8192 # 8KB chunks
    
    # Store standard seek position to read, but check size first
    try:
        # Check size by reading chunks
        while True:
            chunk = upload_file.file.read(chunk_size)
            if not chunk:
                break
            size += len(chunk)
            if size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed limit of {max_size // (1024*1024)}MB."
                )
        
        # Rewind file pointer after reading so we can write it
        upload_file.file.seek(0)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error measuring file size: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating file size limits."
        )

    # 5. Create secure target directory structure inside our uploads directory
    target_dir = settings.UPLOAD_PATH / sub_folder / file_type
    target_dir.mkdir(parents=True, exist_ok=True)

    # 6. Generate a completely randomized secure filename
    secure_filename = f"{uuid.uuid4().hex}{extension}"
    destination_path = target_dir / secure_filename

    # 7. Write the file out in secure blocks
    try:
        with open(destination_path, "wb") as f:
            while True:
                chunk = upload_file.file.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        logger.error(f"Failed writing uploaded file to disk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save uploaded document safely to server storage."
        )
    finally:
        upload_file.file.close()

    # 8. Return relative path for database storing
    relative_path = f"{settings.UPLOAD_DIR}/{sub_folder}/{file_type}/{secure_filename}"
    logger.info(f"Successfully verified and saved secure upload to: {relative_path}")
    return relative_path
