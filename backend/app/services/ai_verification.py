import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger("trust_sell.ai_verification")

CNIC_PATTERN = re.compile(r"^[0-9]{5}-[0-9]{7}-[0-9]{1}$")


@dataclass
class IdentityVerificationResult:
    biometric_match_score: float
    cnic_format_valid: bool
    cnic_database_match: bool
    face_detected_on_selfie: bool
    face_detected_on_cnic: bool
    overall_verified: bool
    rejection_reasons: list
    audit_id: str


def validate_cnic_number(cnic_number: str) -> bool:
    return bool(CNIC_PATTERN.match(cnic_number.strip()))


def _file_fingerprint(path: Path) -> str:
    """Stable hash of image bytes for dev/simulated biometric comparison."""
    if not path.exists():
        return ""
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def _simulate_face_detected(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 500:
        return False
    # Real deployment: AWS Rekognition, Azure Face API, or on-prem CV model
    return path.suffix.lower() in {".jpg", ".jpeg", ".png"}


def verify_identity_documents(
    selfie_path: str,
    cnic_path: str,
    cnic_number: str,
    project_root: Path,
) -> IdentityVerificationResult:
    """
    Biometric + CNIC verification pipeline.
    Production: plug NADRA API + face embedding comparison here.
    """
    reasons = []
    selfie_file = project_root / selfie_path
    cnic_file = project_root / cnic_path

    cnic_valid = validate_cnic_number(cnic_number)
    if not cnic_valid:
        reasons.append("CNIC number format is invalid (expected XXXXX-XXXXXXX-X).")

    face_selfie = _simulate_face_detected(selfie_file)
    face_cnic = _simulate_face_detected(cnic_file)
    if not face_selfie:
        reasons.append("Live selfie could not be validated. Retake in good lighting.")
    if not face_cnic:
        reasons.append("CNIC image is unclear or invalid.")

    selfie_hash = _file_fingerprint(selfie_file)
    cnic_hash = _file_fingerprint(cnic_file)

    # Simulated biometric score: penalize identical files (fraud) and reward valid captures
    if selfie_hash and cnic_hash and selfie_hash == cnic_hash:
        biometric_score = 0.15
        reasons.append("Selfie and CNIC appear identical — possible spoofing.")
    elif face_selfie and face_cnic and cnic_valid:
        # Simulated match score (production: embedding cosine similarity)
        combined = int(selfie_hash[:8], 16) ^ int(cnic_hash[:8], 16)
        biometric_score = 0.72 + (combined % 28) / 100.0
    else:
        biometric_score = 0.35

    # Simulated NADRA cross-reference (production: government API)
    cnic_db_match = cnic_valid and biometric_score >= 0.7

    overall = (
        cnic_valid
        and face_selfie
        and face_cnic
        and biometric_score >= 0.65
        and cnic_db_match
        and len(reasons) == 0
    )

    audit_id = hashlib.sha256(f"{cnic_number}{selfie_hash}".encode()).hexdigest()[:16]
    logger.info(
        f"Identity audit {audit_id}: score={biometric_score:.2f} verified={overall}"
    )

    return IdentityVerificationResult(
        biometric_match_score=round(biometric_score, 3),
        cnic_format_valid=cnic_valid,
        cnic_database_match=cnic_db_match,
        face_detected_on_selfie=face_selfie,
        face_detected_on_cnic=face_cnic,
        overall_verified=overall,
        rejection_reasons=reasons,
        audit_id=audit_id,
    )
