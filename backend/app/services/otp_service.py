import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

logger = logging.getLogger("trust_sell.otp")

# In-memory OTP store (swap for Redis in production)
_otp_store: Dict[str, dict] = {}
_verified_tokens: Dict[str, dict] = {}

OTP_LENGTH = 6
OTP_TTL_MINUTES = 10
OTP_TOKEN_TTL_MINUTES = 30
MAX_ATTEMPTS = 5


def _phone_key(phone: str) -> str:
    return hashlib.sha256(phone.encode()).hexdigest()[:32]


def generate_otp_code() -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(OTP_LENGTH))


def store_otp(phone: str, code: str) -> None:
    key = _phone_key(phone)
    _otp_store[key] = {
        "code": code,
        "attempts": 0,
        "expires_at": datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES),
        "phone": phone,
    }
    logger.info(f"OTP generated for phone ending ...{phone[-4:]}")


def verify_otp(phone: str, code: str) -> Tuple[bool, str]:
    key = _phone_key(phone)
    record = _otp_store.get(key)
    if not record:
        return False, "No OTP request found. Please request a new code."
    if datetime.utcnow() > record["expires_at"]:
        _otp_store.pop(key, None)
        return False, "OTP has expired. Please request a new code."
    if record["attempts"] >= MAX_ATTEMPTS:
        _otp_store.pop(key, None)
        return False, "Too many failed attempts. Request a new OTP."
    if record["code"] != code.strip():
        record["attempts"] += 1
        return False, f"Invalid OTP. {MAX_ATTEMPTS - record['attempts']} attempts remaining."
    _otp_store.pop(key, None)
    token = secrets.token_urlsafe(32)
    _verified_tokens[token] = {
        "phone": phone,
        "expires_at": datetime.utcnow() + timedelta(minutes=OTP_TOKEN_TTL_MINUTES),
    }
    return True, token


def consume_otp_token(token: str, phone: str) -> bool:
    record = _verified_tokens.get(token)
    if not record:
        return False
    if datetime.utcnow() > record["expires_at"]:
        _verified_tokens.pop(token, None)
        return False
    if record["phone"] != phone:
        return False
    _verified_tokens.pop(token, None)
    return True
