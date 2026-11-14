import logging
from fastapi import APIRouter, HTTPException, status
from app.config.settings import settings
from app.schemas.otp import OtpSendRequest, OtpSendResponse, OtpVerifyRequest, OtpVerifyResponse
from app.services.otp_service import generate_otp_code, store_otp, verify_otp
from app.services.verification import normalize_phone

logger = logging.getLogger("trust_sell.otp")
router = APIRouter(prefix="/auth/otp", tags=["OTP Verification"])


@router.post("/send", response_model=OtpSendResponse)
async def send_otp(payload: OtpSendRequest):
    """Send SMS OTP to verify phone ownership before secure signup."""
    phone = normalize_phone(payload.phone)
    if len(phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number.")

    code = generate_otp_code()
    store_otp(phone, code)

    response = OtpSendResponse(
        message=f"OTP sent to {phone[-4:].rjust(len(phone), '*')}",
        expires_in_minutes=10,
    )
    if settings.ENV == "development":
        response.dev_otp = code
        logger.info(f"[DEV] OTP for {phone}: {code}")
    return response


@router.post("/verify", response_model=OtpVerifyResponse)
async def verify_otp_code(payload: OtpVerifyRequest):
    """Verify OTP and receive a one-time token for signup."""
    phone = normalize_phone(payload.phone)
    ok, result = verify_otp(phone, payload.code)
    if not ok:
        raise HTTPException(status_code=400, detail=result)
    return OtpVerifyResponse(
        message="Phone number verified successfully.",
        otp_token=result,
    )
