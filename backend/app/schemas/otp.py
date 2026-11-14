from pydantic import BaseModel, Field


class OtpSendRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)


class OtpSendResponse(BaseModel):
    message: str
    expires_in_minutes: int = 10
    dev_otp: str | None = None


class OtpVerifyRequest(BaseModel):
    phone: str
    code: str = Field(..., min_length=4, max_length=8)


class OtpVerifyResponse(BaseModel):
    message: str
    otp_token: str
    expires_in_minutes: int = 30
