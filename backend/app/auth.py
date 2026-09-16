"""
Authentication and Officer Profile Management for NiyamDrishti AI.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional

from fastapi import Depends, HTTPException, Header, status
from pydantic import BaseModel, Field

TOKEN_EXPIRY_SECONDS = 86400 * 7  # 7 days


def _get_secret_key() -> Optional[str]:
    """Read the signing secret from the environment on every call.

    No default is ever supplied — if AUTH_SECRET_KEY is missing the service
    fails closed (tokens cannot be created or verified).
    """
    return os.environ.get("AUTH_SECRET_KEY")

# Pre-seeded authorized officers matching SIH field operations
OFFICER_REGISTRY: dict[str, dict] = {
    "LMO-DEL-2024-884": {
        "officer_id": "LMO-DEL-2024-884",
        "name": "Rajesh Sharma",
        "pin_hash": hashlib.sha256("8842".encode()).hexdigest(),
        "designation": "Legal Metrology Officer (LMO)",
        "zone": "North Delhi District - Circle 04",
        "station": "Directorate of Legal Metrology, Delhi HQ",
        "role": "inspector",
    },
    "FSO-MH-001": {
        "officer_id": "FSO-MH-001",
        "name": "Suresh Patil",
        "pin_hash": hashlib.sha256("1234".encode()).hexdigest(),
        "designation": "Legal Metrology Inspector",
        "zone": "Mumbai Circle 01",
        "station": "Legal Metrology Bhawan, Mumbai",
        "role": "inspector",
    },
    "DIR-CENTRAL-001": {
        "officer_id": "DIR-CENTRAL-001",
        "name": "Dr. Ananya Roy",
        "pin_hash": hashlib.sha256("9999".encode()).hexdigest(),
        "designation": "Joint Director (Legal Metrology)",
        "zone": "National Enforcement Command",
        "station": "Department of Consumer Affairs, New Delhi",
        "role": "admin",
    },
}


class OfficerProfile(BaseModel):
    officer_id: str
    name: str
    designation: str
    zone: str
    station: str
    role: str


class LoginRequest(BaseModel):
    officer_id: str = Field(..., description="Legal Metrology Officer ID, e.g. LMO-DEL-2024-884")
    pin: str = Field(..., description="Security PIN / Token")
    circle: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    officer: OfficerProfile


def create_token(officer_id: str) -> str:
    secret = _get_secret_key()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "server_configuration",
                "message": "AUTH_SECRET_KEY is not set on the server.",
            },
        )
    payload = {
        "sub": officer_id,
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS,
        "iat": int(time.time()),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
    sig = hmac.new(secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
    return f"{payload_b64}.{sig_b64}"


def verify_token(token: str) -> Optional[str]:
    secret = _get_secret_key()
    if not secret:
        return None
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, sig_b64 = parts
        expected_sig = hmac.new(
            secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256
        ).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode("utf-8").rstrip("=")

        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None

        # Add padding back if necessary
        rem = len(payload_b64) % 4
        padded = payload_b64 + ("=" * (4 - rem) if rem else "")
        payload = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))

        if payload.get("exp", 0) < time.time():
            return None

        return payload.get("sub")
    except Exception:
        return None


def authenticate_officer(req: LoginRequest) -> Optional[dict]:
    officer = OFFICER_REGISTRY.get(req.officer_id.strip())
    if not officer:
        return None
    entered_hash = hashlib.sha256(req.pin.strip().encode()).hexdigest()
    if not hmac.compare_digest(entered_hash, officer["pin_hash"]):
        return None
    return officer


def get_officer_by_token(token: str) -> Optional[OfficerProfile]:
    """Return the officer profile for a raw bearer token, or None if invalid."""
    officer_id = verify_token(token)
    if not officer_id or officer_id not in OFFICER_REGISTRY:
        return None
    raw = OFFICER_REGISTRY[officer_id]
    return OfficerProfile(
        officer_id=raw["officer_id"],
        name=raw["name"],
        designation=raw["designation"],
        zone=raw["zone"],
        station=raw["station"],
        role=raw["role"],
    )


def get_current_officer(authorization: Optional[str] = Header(None)) -> Optional[OfficerProfile]:
    """Dependency that extracts the officer profile if Authorization header is provided."""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return get_officer_by_token(parts[1])


def require_auth(officer: Optional[OfficerProfile] = Depends(get_current_officer)) -> OfficerProfile:
    """Dependency used on endpoints that MUST have an authenticated officer."""
    if officer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": "Authentication token missing or expired"},
        )
    return officer
