import logging
from datetime import datetime, timedelta
from typing import List, Optional
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie, APIKeyHeader
from jose import JWTError, jwt
from app.config.settings import settings
from app.config.db import get_collection
from bson import ObjectId

logger = logging.getLogger("trust_sell.security")

# Support retrieving access token from authorization header OR cookie for max security flex
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)
header_scheme = APIKeyHeader(name="Authorization", auto_error=False)

# Password Cryptography Utilities using native bcrypt
def get_password_hash(password: str) -> str:
    """Generate a secure, high-entropy bcrypt hash for passwords."""
    salt = bcrypt.gensalt(rounds=12)  # High work factor for security
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), 
            hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

# JWT Utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT containing authentication claims, expired after duration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Store token metadata (expiration, subject details)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns payload or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT Token validation failed: {str(e)}")
        return None

# FastAPI Route Security Dependencies
async def get_current_user(
    cookie_token: Optional[str] = Depends(cookie_scheme),
    header_token: Optional[str] = Depends(header_scheme)
) -> dict:
    """
    Dependency to authenticate and retrieve the current active user from JWT.
    Supports either an HttpOnly Cookie named 'access_token' or an 'Authorization' header.
    """
    token = None
    
    # 1. Check Cookie first (recommended for web applications)
    if cookie_token:
        token = cookie_token
        # In case cookie value starts with Bearer prefix
        if token.startswith("Bearer "):
            token = token[7:]
            
    # 2. Check Authorization Header if cookie not found (recommended for APIs/Mobile clients)
    elif header_token:
        token = header_token
        # Strip 'Bearer ' prefix if present
        if token.startswith("Bearer ") or token.startswith("bearer "):
            token = token[7:]

    # If no token is provided, raise 401 Unauthorized
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate token claims
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or session has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    role = payload.get("role")
    
    try:
        # Validate ObjectId structure
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed credentials identifier.",
            )
        
        users_collection = get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account no longer exists.",
            )
            
        # Security check: verify status matches token payload claims
        if user.get("role") != role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session parameters do not match database status. Re-authenticate.",
            )
            
        # Clean user document of sensitive system parameters before passing to handlers
        user["_id"] = str(user["_id"])
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal database lookup error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating account credentials.",
        )

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency ensuring the authenticated user is currently active/enabled."""
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )
    return current_user

class RequireRole:
    """
    Callable dependency class to enforce Role-Based Access Control (RBAC).
    Usage: Depends(RequireRole(["seller", "admin"]))
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict = Depends(get_current_active_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in self.allowed_roles:
            logger.warning(f"Access denied to user {current_user.get('email')} with role {user_role}. Required: {self.allowed_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. This action requires one of the following privileges: {', '.join(self.allowed_roles)}."
            )
        return current_user
