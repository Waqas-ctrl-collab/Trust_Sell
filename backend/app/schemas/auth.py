from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserResponse

class LoginRequest(BaseModel):
    """View schema for incoming user credentials."""
    email: EmailStr
    password: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    """View schema returned to client upon successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
