import logging
import re
from dataclasses import dataclass
from typing import List

logger = logging.getLogger("trust_sell.fraud")

SCAM_PATTERNS = [
    (r"https?://", "External link detected — stay on TrustSell for safe payments."),
    (r"whatsapp\.com|wa\.me|t\.me|telegram", "Off-platform contact request."),
    (r"advance\s*payment|pay\s*first|send\s*money", "Advance payment pressure tactic."),
    (r"otp|verification\s*code|bank\s*pin", "Request for sensitive codes."),
    (r"western\s*union|crypto|bitcoin|binance", "High-risk payment method mentioned."),
    (r"urgent|act\s*now|limited\s*time", "Urgency pressure language."),
]


@dataclass
class FraudAnalysis:
    is_safe: bool
    risk_score: float
    flags: List[str]
    sanitized_message: str
    blocked: bool


def analyze_chat_message(text: str) -> FraudAnalysis:
    """Escrow fraud filter — scans messages before delivery."""
    lowered = text.lower().strip()
    flags = []
    risk = 0.0

    for pattern, message in SCAM_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE):
            flags.append(message)
            risk += 0.2

    if len(lowered) > 500:
        flags.append("Unusually long message.")
        risk += 0.1

    risk = min(risk, 1.0)
    blocked = risk >= 0.6
    is_safe = not blocked and risk < 0.4

    if flags:
        logger.warning(f"Chat fraud scan: risk={risk:.2f} flags={flags}")

    return FraudAnalysis(
        is_safe=is_safe,
        risk_score=round(risk, 2),
        flags=flags,
        sanitized_message=text,
        blocked=blocked,
    )
