"""
NiyamDrishti Backend — FastAPI Application

Endpoints implemented:
  Phase 1:  GET  /health
  Phase 2:  POST /inspection                       → Create inspection (DB)
            GET  /inspection/{inspection_id}        → Get one inspection (DB)
  Phase 7:  GET  /inspections                       → List (PostgreSQL)
            GET  /dashboard                         → Stats (PostgreSQL)
            GET  /inspection/{inspection_id}/report → Full report (PostgreSQL)
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, File, HTTPException, Header, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import (
    LoginRequest,
    LoginResponse,
    OfficerProfile,
    authenticate_officer,
    create_token,
    get_current_officer,
    get_officer_by_token,
    require_auth,
)
from app.database import create_tables, get_db
from app.models import Declaration as DeclarationModel
from app.models import Inspection, Review as ReviewModel, Rule, Violation as ViolationModel
from app.seed_rules import seed_rules
from app.services.ai_ocr import analyze_package_label
from app.services.rule_engine import evaluate_rules
from app.services.rule_version_resolver import get_current_rules
from app.schemas import (
    AIAnalysis,
    AnalyzeInspectionResponse,
    CheckResult,
    ComplianceCheck,
    CreateInspectionRequest,
    CurrentRulesResponse,
    DashboardResponse,
    DashboardStats,
    Declaration,
    Evidence,
    InspectionDetail,
    InspectionListResponse,
    InspectionReport,
    InspectionStatus,
    InspectionSummary,
    InspectorDecision,
    InspectorInfo,
    OCRDeclarationsPayload,
    OCRField,
    ProductInfo,
    ReviewInspectionRequest,
    ReviewInspectionResponse,
    RuleOut,
    Severity,
    Violation,
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="NiyamDrishti API",
    description="Regulatory Compliance Inspection Platform — Legal Metrology Division",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# CORS – explicit, configurable origins via CORS_ORIGINS env var.
# Supports a comma-separated list of allowed origins.
# If CORS_ORIGINS contains "*" (the only case where credentials are disabled),
# the middleware allows all origins for development convenience.
# ---------------------------------------------------------------------------

def _parse_cors_origins() -> list[str]:
    raw = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    )
    origins = [o.strip() for o in raw.replace(";", ",").split(",") if o.strip()]
    return origins or [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


_cors_origins = _parse_cors_origins()
_cors_wildcard = "*" in _cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _cors_wildcard else _cors_origins,
    allow_credentials=not _cors_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Evidence Storage Setup
# ---------------------------------------------------------------------------

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
EVIDENCE_DIR = os.path.join(UPLOAD_DIR, "evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# Paths that can appear in the generated filename (lower-case only).
_SAFE_PANEL_TYPES = {"primary", "mrp", "manufacturer", "back", "front", "other"}
_SAFE_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _safe_evidence_filename(panel_type: str, original_filename: str, content_type: str | None) -> str:
    """Build a server-generated filename that resists traversal and enumeration."""
    panel = re.sub(r"[^a-z0-9_-]", "", (panel_type or "primary").lower().strip()) or "primary"
    ext = ""
    if original_filename:
        maybe_ext = os.path.splitext(original_filename)[1].lower()
        if maybe_ext in _SAFE_IMAGE_EXTS:
            ext = maybe_ext
    if not ext and content_type:
        _mime_to_ext = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/bmp": ".bmp",
        }
        ext = _mime_to_ext.get(content_type.split(";")[0].strip(), "")
    if not ext:
        ext = ".jpg"
    ts = int(datetime.now(timezone.utc).timestamp())
    return f"{panel}_{ts}_{uuid.uuid4().hex[:8]}{ext}"


@app.get(
    "/uploads/evidence/{inspection_id}/{filename}",
    tags=["Evidence"],
    summary="Retrieve an inspection evidence photo (authenticated)",
)
def get_evidence_file(
    inspection_id: str,
    filename: str,
    token: Optional[str] = Query(None, description="Bearer token for <img>-tag access"),
    authorization: Optional[str] = Header(None),
):
    """Serve a stored evidence photo.

    Access requires a valid officer token supplied via the Authorization header
    or the ``token`` query parameter (the latter keeps plain ``<img src>``
    rendering working from the React dashboard).  '.'/directory traversal is
    rejected and every lookup is constrained to the evidence directory.
    """
    officer = get_current_officer(authorization)
    if officer is None and token:
        officer = get_officer_by_token(token)
    if officer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": "Authentication token missing or expired"},
        )

    if not re.fullmatch(r"[A-Za-z0-9_-]+", inspection_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_path", "message": "Invalid inspection identifier."},
        )
    if not re.fullmatch(r"[A-Za-z0-9!()@._\-]+", filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_path", "message": "Invalid evidence filename."},
        )

    target = os.path.realpath(os.path.join(EVIDENCE_DIR, inspection_id, filename))
    evidence_root = os.path.realpath(EVIDENCE_DIR)
    if os.path.commonpath([target, evidence_root]) != evidence_root or not os.path.isfile(target):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "evidence_not_found", "message": "Evidence file not found."},
        )
    return FileResponse(target, media_type="image/jpeg")


@app.on_event("startup")
def on_startup():
    """Create database tables and auto-seed verified Legal Metrology rules."""
    create_tables()
    try:
        seed_rules()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Helper: generate a unique inspection ID like "INS-20260911-a3f1"
# ---------------------------------------------------------------------------

def _generate_inspection_id() -> str:
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:4]
    return f"INS-{date_part}-{short_uuid}"


# ---------------------------------------------------------------------------
# Helper: convert an Inspection ORM object → InspectionDetail response
# ---------------------------------------------------------------------------

def _inspection_to_detail(insp: Inspection) -> dict:
    """
    Convert a SQLAlchemy Inspection (with loaded relationships)
    into a dict that matches InspectionDetail schema.
    """
    return {
        "inspection_id": insp.inspection_id,
        "product_name": insp.product_name,
        "inspector_id": insp.inspector_id,
        "inspection_date": insp.inspection_date,
        "rule_version": insp.rule_version,
        "overall_status": insp.overall_status,
        "confidence": insp.confidence,
        "is_ecommerce": insp.is_ecommerce,
        "created_at": insp.created_at,
        "updated_at": insp.updated_at,
        "declarations": [
            {
                "id": d.id,
                "field_name": d.field_name,
                "value": d.value,
                "confidence": d.confidence,
                "bbox": d.bbox,
                "source": d.source,
            }
            for d in insp.declarations
        ],
        "violations": [
            {
                "id": v.id,
                "rule_id": v.rule_id,
                "field_name": v.field_name,
                "severity": v.severity,
                "status": v.status,
                "reason": v.reason,
                "evidence_image": v.evidence_image,
                "bbox": v.bbox,
                "extracted_text": v.extracted_text,
                "confidence": v.confidence,
            }
            for v in insp.violations
        ],
        "reviews": [
            {
                "id": r.id,
                "decision": r.decision,
                "comment": r.comment,
                "reviewed_at": r.reviewed_at,
                "reviewer_id": r.reviewer_id,
            }
            for r in insp.reviews
        ],
    }


# ---------------------------------------------------------------------------
# Helpers: convert DB Inspection rows into Phase 7 response shapes
# (dashboard / list / report are now PostgreSQL-backed)
# ---------------------------------------------------------------------------

# DB uses uppercase status values; the shared schemas expect lowercase enums.
_SQL_STATUS_TO_ENUM = {
    "PASS": InspectionStatus.COMPLIANT,
    "FAIL": InspectionStatus.VIOLATION,
    "REVIEW_REQUIRED": InspectionStatus.REVIEW_REQUIRED,
    "PENDING": InspectionStatus.PENDING,
}

_ENUM_STATUS_TO_SQL = {v: k for k, v in _SQL_STATUS_TO_ENUM.items()}

_SQL_DECISION_TO_ENUM = {
    "PASS": InspectorDecision.APPROVED,
    "FAIL": InspectorDecision.REJECTED,
    "REVIEW_REQUIRED": InspectorDecision.ESCALATED,
}


def _status_to_enum(status: str | None) -> InspectionStatus:
    return _SQL_STATUS_TO_ENUM.get(status, InspectionStatus.PENDING)


def _review_decision(insp: Inspection) -> InspectorDecision:
    if insp.reviews:
        latest = insp.reviews[-1]
        return _SQL_DECISION_TO_ENUM.get(latest.decision, InspectorDecision.PENDING_REVIEW)
    return InspectorDecision.PENDING_REVIEW


def _inspection_to_summary(
    insp: Inspection,
    violation_count: int,
    decision: InspectorDecision,
) -> InspectionSummary:
    """Lightweight summary row for GET /inspections and GET /dashboard."""
    return InspectionSummary(
        id=insp.inspection_id,
        product=ProductInfo(
            id=insp.inspection_id,
            name=insp.product_name,
            category="packaged commodity",
        ),
        inspector=InspectorInfo(
            id=insp.inspector_id,
            name=insp.inspector_id,
            badge_number=insp.inspector_id,
        ),
        status=_status_to_enum(insp.overall_status),
        date=insp.inspection_date or insp.created_at,
        ai_confidence=insp.confidence if insp.confidence is not None else 0.0,
        violation_count=violation_count,
        inspector_decision=decision,
    )


def _inspection_to_report(insp: Inspection, totals: dict) -> InspectionReport:
    """Full report shape for GET /inspection/{inspection_id}/report."""
    status_enum = _status_to_enum(insp.overall_status)
    latest_review = insp.reviews[-1] if insp.reviews else None
    decision = _review_decision(insp)

    declarations = [
        Declaration(
            id=str(d.id),
            field_name=d.field_name,
            declared_value=d.value or "",
            verified=d.confidence is not None,
            notes=(
                f"confidence={d.confidence}; bbox={d.bbox}; source={d.source}"
                if d.confidence is not None or d.bbox is not None
                else f"source={d.source}"
            ),
        )
        for d in insp.declarations
    ]

    checks = [
        ComplianceCheck(
            id=str(v.id),
            rule_code=v.rule_id,
            description=v.reason or v.rule_id,
            result=CheckResult.FAIL,
            details=v.field_name,
        )
        for v in insp.violations
    ]
    if not checks:
        checks.append(
            ComplianceCheck(
                id="chk-overall",
                rule_code="OVERALL",
                description="No open violations recorded",
                result=CheckResult.PASS,
                details=insp.overall_status,
            )
        )

    violations = [
        Violation(
            id=str(v.id),
            rule_code=v.rule_id,
            description=v.reason or v.rule_id,
            severity=Severity(v.severity) if v.severity in {s.value for s in Severity} else Severity.MEDIUM,
            recommended_action=None,
        )
        for v in insp.violations
    ]

    evidence = [
        Evidence(
            id=f"ev-{v.id}",
            type="photo",
            url=v.evidence_image,
            description=v.reason,
            captured_at=insp.inspection_date,
        )
        for v in insp.violations
        if v.evidence_image
    ]

    findings = [
        f"{len(insp.declarations)} declaration(s) extracted",
        f"{len(insp.violations)} violation(s) recorded",
    ]

    return InspectionReport(
        inspection_id=insp.inspection_id,
        product=ProductInfo(
            id=insp.inspection_id,
            name=insp.product_name,
            category="packaged commodity",
        ),
        inspector=InspectorInfo(
            id=insp.inspector_id,
            name=insp.inspector_id,
            badge_number=insp.inspector_id,
        ),
        date=insp.inspection_date or insp.created_at or datetime.now(timezone.utc),
        rule_version=insp.rule_version or "N/A",
        status=status_enum,
        declarations=declarations,
        checks=checks,
        violations=violations,
        evidence=evidence,
        ai_analysis=AIAnalysis(
            confidence_score=insp.confidence if insp.confidence is not None else 0.0,
            model_version="niyam-ai-v1.2",
            findings=findings,
            suggested_status=status_enum,
        ),
        inspector_decision=decision,
        inspector_remarks=latest_review.comment if latest_review else None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health", tags=["System"])
def health_check():
    """Simple health check."""
    return {"status": "ok", "version": "1.0.0"}


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION & OFFICER PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/auth/login", response_model=LoginResponse, tags=["Authentication"])
def login(req: LoginRequest):
    """Authenticate officer via Officer ID and security PIN."""
    officer = authenticate_officer(req)
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials", "message": "Invalid Officer ID or Security PIN"},
        )
    token = create_token(officer["officer_id"])
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=86400 * 7,
        officer=OfficerProfile(
            officer_id=officer["officer_id"],
            name=officer["name"],
            designation=officer["designation"],
            zone=officer["zone"],
            station=officer["station"],
            role=officer["role"],
        ),
    )


@app.get("/auth/me", response_model=Optional[OfficerProfile], tags=["Authentication"])
def get_me(officer: Optional[OfficerProfile] = Depends(get_current_officer)):
    """Retrieve profile of currently authenticated officer."""
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": "Authentication token missing or expired"},
        )
    return officer


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: INSPECTION CRUD (database-backed)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post(
    "/inspection",
    response_model=InspectionDetail,
    status_code=201,
    tags=["Inspections"],
    summary="Create a new inspection",
    description="Creates a new inspection record in the database. "
                "Returns the created inspection with its generated ID. "
                "Status starts as PENDING — analysis happens in a later step.",
)
def post_create_inspection(
    body: CreateInspectionRequest,
    officer: OfficerProfile = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Authenticated route handler for creating a new inspection."""
    return create_inspection(body, db, officer=officer)


def create_inspection(
    body: CreateInspectionRequest,
    db: Session,
    officer: Optional[OfficerProfile] = None,
):
    """Logic for creating a new Inspection row.

    When called from the API, ``officer`` is the authenticated officer.
    ``officer.officer_id`` takes precedence over ``body.inspector_id`` so the
    recorded inspector identity always matches the token.
    """
    inspector_id = (officer.officer_id if officer else None) or body.inspector_id
    # Create a new Inspection row
    new_inspection = Inspection(
        inspection_id=_generate_inspection_id(),
        product_name=body.product_name,
        inspector_id=inspector_id,
        overall_status="PENDING",
        is_ecommerce=body.is_ecommerce,
    )

    db.add(new_inspection)
    db.commit()
    db.refresh(new_inspection)  # reload to get defaults (created_at, etc.)

    return _inspection_to_detail(new_inspection)


@app.get(
    "/inspection/{inspection_id}",
    response_model=InspectionDetail,
    tags=["Inspections"],
    summary="Get one inspection",
    description="Retrieves a single inspection by its ID, including "
                "declarations, violations, and reviews.",
)
def get_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    insp = (
        db.query(Inspection)
        .filter(Inspection.inspection_id == inspection_id)
        .first()
    )

    if insp is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "inspection_not_found",
                "message": f"No inspection found with ID '{inspection_id}'",
            },
        )

    return _inspection_to_detail(insp)


# ═══════════════════════════════════════════════════════════════════════════════
# SPRINT 1: RULE REPOSITORY + DETERMINISTIC OCR ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def _rule_to_output(rule: Rule) -> dict:
    return {
        "id": rule.id,
        "rule_id": rule.rule_id,
        "version": rule.version,
        "field_name": rule.field_name,
        "requirement_type": rule.requirement_type,
        "requirement": rule.requirement,
        "severity": rule.severity,
        "explanation": rule.explanation,
        "source_reference": rule.source_reference,
        "effective_from": rule.effective_from,
        "effective_to": rule.effective_to,
        "active": rule.active,
    }


@app.get("/rules", response_model=list[RuleOut], tags=["Rules"])
def list_rules(
    active: bool | None = Query(None, description="Optionally filter by active state"),
    db: Session = Depends(get_db),
):
    """List versioned rules stored by the legal-team import process."""
    query = db.query(Rule).order_by(Rule.version.desc(), Rule.rule_id.asc())
    if active is not None:
        query = query.filter(Rule.active.is_(active))
    return [_rule_to_output(rule) for rule in query.all()]


@app.get("/rules/current", response_model=CurrentRulesResponse, tags=["Rules"])
def current_rules(db: Session = Depends(get_db)):
    """Return only the active, effective version selected from database data."""
    version, rules = get_current_rules(db)
    if version is None:
        return CurrentRulesResponse(
            warning="No active, legally verified rules are available. LEGAL SOURCE VERIFICATION REQUIRED"
        )
    return CurrentRulesResponse(rule_version=version, rules=[_rule_to_output(rule) for rule in rules])


@app.post(
    "/inspection/{inspection_id}/analyze",
    response_model=AnalyzeInspectionResponse,
    tags=["Inspections"],
    summary="Persist structured OCR facts and run deterministic rule evaluation",
)
def analyze_inspection(
    inspection_id: str,
    payload: OCRDeclarationsPayload,
    officer: OfficerProfile = Depends(require_auth),
    is_ecommerce: Optional[bool] = Query(None, description="True = e-commerce listing; False = physical package; None = unconfirmed"),
    db: Session = Depends(get_db),
):
    """Analyze structured OCR output; AI provides facts, rules decide compliance."""
    inspection = db.query(Inspection).filter(Inspection.inspection_id == inspection_id).first()
    if inspection is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "inspection_not_found", "message": f"No inspection found with ID '{inspection_id}'"},
        )

    effective_is_ecommerce = is_ecommerce if is_ecommerce is not None else inspection.is_ecommerce

    rule_version, rules = get_current_rules(db)
    result = evaluate_rules(payload.root, rules, rule_version, is_ecommerce=effective_is_ecommerce)

    # Re-analysis replaces machine-generated extraction/evaluation rows while
    # deliberately preserving human review history.
    db.query(DeclarationModel).filter(DeclarationModel.inspection_id == inspection_id).delete(
        synchronize_session=False
    )
    db.query(ViolationModel).filter(ViolationModel.inspection_id == inspection_id).delete(
        synchronize_session=False
    )

    for field_name, field in payload.root.items():
        db.add(
            DeclarationModel(
                inspection_id=inspection_id,
                field_name=field_name,
                value=None if field.value is None else str(field.value),
                confidence=field.confidence,
                bbox=json.dumps(field.bbox) if field.bbox is not None else None,
                source=field.source,
            )
        )

    persisted_violations: list[ViolationModel] = []
    for violation in result["violations"]:
        field = payload.root.get(violation["field"])
        db_violation = ViolationModel(
            inspection_id=inspection_id,
            rule_id=violation["rule_id"],
            field_name=violation["field"],
            severity=violation["severity"],
            status="open",
            reason=violation["reason"],
            evidence_image=field.evidence_image if field is not None else None,
            bbox=json.dumps(field.bbox) if field is not None and field.bbox is not None else None,
            extracted_text=violation["value"],
            confidence=violation["confidence"],
        )
        db.add(db_violation)
        persisted_violations.append(db_violation)

    confidences = [field.confidence for field in payload.root.values() if field.confidence is not None]
    inspection.rule_version = result["rule_version"]
    inspection.overall_status = result["overall_status"]
    inspection.confidence = sum(confidences) / len(confidences) if confidences else None
    inspection.is_ecommerce = effective_is_ecommerce
    db.commit()
    for violation in persisted_violations:
        db.refresh(violation)

    return {
        "inspection_id": inspection_id,
        "overall_status": result["overall_status"],
        "rule_version": result["rule_version"],
        "confidence": inspection.confidence,
        "is_ecommerce": inspection.is_ecommerce,
        "checks": result["checks"],
        "violations": [
            {
                "id": violation.id,
                "rule_id": violation.rule_id,
                "field_name": violation.field_name,
                "severity": violation.severity,
                "status": violation.status,
                "reason": violation.reason,
                "evidence_image": violation.evidence_image,
                "bbox": violation.bbox,
                "extracted_text": violation.extracted_text,
                "confidence": violation.confidence,
            }
            for violation in persisted_violations
        ],
        "warnings": result["warnings"],
    }


@app.post(
    "/inspection/{inspection_id}/evidence",
    tags=["Inspections"],
    summary="Upload package label evidence image and execute AI/OCR & compliance evaluation",
)
async def upload_inspection_evidence(
    inspection_id: str,
    file: UploadFile = File(...),
    panel_type: str = Query("primary", description="Panel type: primary, mrp, manufacturer, back, front"),
    is_ecommerce: Optional[bool] = Query(None, description="True = e-commerce listing; False = physical package; None = unconfirmed"),
    db: Session = Depends(get_db),
    officer: OfficerProfile = Depends(require_auth),
):
    """
    Accepts raw label image, runs quality check, OCR preprocessing,
    extracts Legal Metrology declarations, and evaluates compliance deterministically.

    Evidence panels accumulate: a new panel is merged with previously uploaded
    declarations (deduplicated per field by highest OCR confidence) instead of
    replacing prior scan data.
    """
    inspection = db.query(Inspection).filter(Inspection.inspection_id == inspection_id).first()
    if inspection is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "inspection_not_found", "message": f"No inspection found with ID '{inspection_id}'"},
        )

    # Validate the upload before persisting anything to disk.
    if file.content_type and not file.content_type.lower().split(";")[0].strip().startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_image_file", "message": "Uploaded file is not an image."},
        )
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "empty_file", "message": "Uploaded file is empty."},
        )

    # Run unified AI/OCR pipeline (raises ValueError on corrupt/non-image bytes).
    try:
        ai_result = analyze_package_label(contents)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_image_file", "message": str(exc)},
        )

    # Save evidence file safely with a server-generated filename.
    insp_evidence_dir = os.path.join(EVIDENCE_DIR, inspection_id)
    os.makedirs(insp_evidence_dir, exist_ok=True)
    clean_filename = _safe_evidence_filename(panel_type, file.filename, file.content_type)
    file_path = os.path.join(insp_evidence_dir, clean_filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    evidence_url = f"/uploads/evidence/{inspection_id}/{clean_filename}"

    # Convert extracted declarations to OCRField mapping
    new_facts: dict[str, OCRField] = {}
    for fname, fval in ai_result["declarations"].items():
        new_facts[fname] = OCRField(
            value=fval["value"],
            confidence=fval["confidence"],
            bbox=fval["bbox"],
            source="ocr",
            evidence_image=evidence_url,
        )

    # Context: explicit query flag wins; otherwise inherit from the inspection record.
    effective_is_ecommerce = is_ecommerce if is_ecommerce is not None else inspection.is_ecommerce
    if is_ecommerce is not None:
        inspection.is_ecommerce = effective_is_ecommerce

    # ── Multi-panel merge: combine this panel with previously stored fields ─────
    existing = (
        db.query(DeclarationModel)
        .filter(DeclarationModel.inspection_id == inspection_id)
        .all()
    )
    existing_by_field = {d.field_name: d for d in existing}
    all_field_names = set(existing_by_field.keys()) | set(new_facts.keys())

    merged_decls: list[dict] = []
    merged_facts: dict[str, OCRField] = {}

    for fname in all_field_names:
        old = existing_by_field.get(fname)
        new = new_facts.get(fname)

        if old is not None and new is None:
            pick = OCRField(
                value=old.value,
                confidence=old.confidence,
                bbox=json.loads(old.bbox) if old.bbox else None,
                source=old.source,
                evidence_image=None,
            )
        elif old is None and new is not None:
            pick = new
        else:
            # Both present — keep the higher-confidence reading (deterministic).
            keep_new = old.confidence is None or (
                new.confidence is not None and new.confidence >= old.confidence
            )
            if keep_new:
                pick = new
            else:
                pick = OCRField(
                    value=old.value,
                    confidence=old.confidence,
                    bbox=json.loads(old.bbox) if old.bbox else None,
                    source=old.source,
                    evidence_image=None,
                )

        merged_facts[fname] = pick
        merged_decls.append(
            {
                "field_name": fname,
                "value": None if pick.value is None else str(pick.value),
                "confidence": pick.confidence,
                "bbox": json.dumps(pick.bbox) if pick.bbox is not None else None,
                "source": pick.source,
            }
        )

    # Replace stored declarations/violations with the merged set (reviews are
    # deliberately left untouched — they are human decisions, not machine rows).
    db.query(DeclarationModel).filter(DeclarationModel.inspection_id == inspection_id).delete(
        synchronize_session=False
    )
    db.query(ViolationModel).filter(ViolationModel.inspection_id == inspection_id).delete(
        synchronize_session=False
    )
    # Drop the now-stale loaded rows from the identity map so freshly flushed
    # replacement rows do not collide with recycled primary keys (SQLite reuses
    # rowids after bulk deletes; expunge detaches the old objects completely).
    for stale in existing:
        db.expunge(stale)

    persisted_declarations = []
    for entry in merged_decls:
        decl = DeclarationModel(inspection_id=inspection_id, **entry)
        db.add(decl)
        persisted_declarations.append(decl)

    # Run deterministic rule engine against the merged declarations.
    rule_version, rules = get_current_rules(db)
    compliance_result = evaluate_rules(merged_facts, rules, rule_version, is_ecommerce=effective_is_ecommerce)

    persisted_violations: list[ViolationModel] = []
    for violation in compliance_result["violations"]:
        field = merged_facts.get(violation["field"])
        db_violation = ViolationModel(
            inspection_id=inspection_id,
            rule_id=violation["rule_id"],
            field_name=violation["field"],
            severity=violation["severity"],
            status="open",
            reason=violation["reason"],
            evidence_image=field.evidence_image if field is not None else None,
            bbox=json.dumps(field.bbox) if field is not None and field.bbox is not None else None,
            extracted_text=violation["value"],
            confidence=violation["confidence"],
        )
        db.add(db_violation)
        persisted_violations.append(db_violation)

    # Update product name if detected
    if new_facts.get("product_name") and new_facts["product_name"].value:
        if inspection.product_name in ("Pending Scan", "Quick Inspection", "Packaged Commodity"):
            inspection.product_name = str(new_facts["product_name"].value)

    confidences = [f.confidence for f in merged_facts.values() if f.confidence is not None]
    inspection.rule_version = compliance_result["rule_version"]
    inspection.overall_status = compliance_result["overall_status"]
    inspection.confidence = sum(confidences) / len(confidences) if confidences else 0.85
    db.commit()

    return {
        "inspection_id": inspection_id,
        "product_name": inspection.product_name,
        "overall_status": compliance_result["overall_status"],
        "rule_version": compliance_result["rule_version"],
        "confidence": inspection.confidence,
        "is_ecommerce": inspection.is_ecommerce,
        "evidence_url": evidence_url,
        "quality_metrics": ai_result["quality_metrics"],
        "ocr_engine": ai_result["ocr_engine"],
        "ocr_confidence_percent": ai_result["ocr_confidence_percent"],
        "raw_text": ai_result["raw_text"],
        "ocr_lines": ai_result["ocr_lines"],
        "checks": compliance_result["checks"],
        "violations": [
            {
                "id": v.id,
                "rule_id": v.rule_id,
                "field_name": v.field_name,
                "severity": v.severity,
                "status": v.status,
                "reason": v.reason,
                "evidence_image": v.evidence_image,
                "bbox": v.bbox,
                "extracted_text": v.extracted_text,
                "confidence": v.confidence,
            }
            for v in persisted_violations
        ],
        "declarations": [
            {
                "id": d.id,
                "field_name": d.field_name,
                "value": d.value,
                "confidence": d.confidence,
                "bbox": d.bbox,
                "source": d.source,
            }
            for d in persisted_declarations
        ],
        "review_required": ai_result["review_required"],
        "review_reasons": ai_result["review_reasons"],
        "warnings": compliance_result["warnings"],
    }


@app.post(
    "/inspection/quick-scan",
    tags=["Inspections"],
    summary="One-step inspection: create record, upload image, run AI/OCR & compliance evaluation",
)
async def quick_scan_inspection(
    file: UploadFile = File(...),
    product_name: str = Query("Packaged Commodity", description="Initial product name"),
    inspector_id: str = Query("LMO-DEL-2024-884", description="Inspector ID (authenticated officer takes precedence)"),
    is_ecommerce: Optional[bool] = Query(None, description="True = e-commerce listing; False = physical package; None = unconfirmed"),
    db: Session = Depends(get_db),
    officer: OfficerProfile = Depends(require_auth),
):
    """Direct one-shot scan endpoint for mobile app and rapid field inspection."""
    new_insp = Inspection(
        inspection_id=_generate_inspection_id(),
        product_name=product_name,
        inspector_id=officer.officer_id if officer else inspector_id,
        overall_status="PENDING",
        is_ecommerce=is_ecommerce,
    )
    db.add(new_insp)
    db.commit()
    db.refresh(new_insp)

    try:
        return await upload_inspection_evidence(
            inspection_id=new_insp.inspection_id,
            file=file,
            panel_type="primary",
            is_ecommerce=is_ecommerce,
            db=db,
            officer=officer,
        )
    except HTTPException:
        # Invalid/invalid-content uploads must not leave orphan PENDING records.
        db.delete(new_insp)
        db.commit()
        raise


@app.post(
    "/inspection/{inspection_id}/review",
    response_model=ReviewInspectionResponse,
    tags=["Inspections"],
    summary="Record an inspector decision",
)
def post_review_inspection(
    inspection_id: str,
    body: ReviewInspectionRequest,
    officer: OfficerProfile = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Authenticated route handler that records an inspector decision."""
    return review_inspection(inspection_id, body, db, officer=officer)


def review_inspection(
    inspection_id: str,
    body: ReviewInspectionRequest,
    db: Session,
    officer: Optional[OfficerProfile] = None,
):
    """Persist a human review and set inspection overall_status to that decision."""
    inspection = db.query(Inspection).filter(Inspection.inspection_id == inspection_id).first()
    if inspection is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "inspection_not_found",
                "message": f"No inspection found with ID '{inspection_id}'",
            },
        )

    reviewer_id = officer.officer_id if officer else body.reviewer_id
    review = ReviewModel(
        inspection_id=inspection_id,
        decision=body.decision,
        comment=body.comment,
        reviewer_id=reviewer_id,
    )
    inspection.overall_status = body.decision
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "inspection_id": inspection_id,
        "overall_status": inspection.overall_status,
        "review": {
            "id": review.id,
            "decision": review.decision,
            "comment": review.comment,
            "reviewed_at": review.reviewed_at,
            "reviewer_id": review.reviewer_id,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7: LIST / DASHBOARD / REPORT (PostgreSQL-backed)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get(
    "/inspections",
    response_model=InspectionListResponse,
    tags=["Inspections"],
    summary="List all inspections",
    description="Returns a paginated list of inspections from PostgreSQL, "
                "most recent first. Supports optional filtering by status.",
)
def list_inspections(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: InspectionStatus | None = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    query = db.query(Inspection)
    if status is not None:
        sql_status = _ENUM_STATUS_TO_SQL.get(status)
        if sql_status is not None:
            query = query.filter(Inspection.overall_status == sql_status)

    total = query.count()

    inspections = (
        query.order_by(
            Inspection.inspection_date.desc(),
            Inspection.created_at.desc(),
            Inspection.inspection_id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    ids = [insp.inspection_id for insp in inspections]
    violation_counts: dict[str, int] = {}
    if ids:
        violation_counts = {
            row[0]: row[1]
            for row in (
                db.query(ViolationModel.inspection_id, func.count(ViolationModel.id))
                .filter(ViolationModel.inspection_id.in_(ids))
                .group_by(ViolationModel.inspection_id)
                .all()
            )
        }

    summaries = [
        _inspection_to_summary(insp, violation_counts.get(insp.inspection_id, 0), _review_decision(insp))
        for insp in inspections
    ]

    return InspectionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        inspections=summaries,
    )


@app.get(
    "/dashboard",
    response_model=DashboardResponse,
    tags=["Dashboard"],
    summary="Dashboard overview",
    description="Returns aggregate statistics computed from PostgreSQL "
                "and the most recent inspections.",
)
def get_dashboard(
    recent_count: int = Query(10, ge=1, le=50, description="Number of recent inspections to return"),
    db: Session = Depends(get_db),
):
    compliant = db.query(Inspection).filter(Inspection.overall_status == "PASS").count()
    violations = db.query(Inspection).filter(Inspection.overall_status == "FAIL").count()
    review_required = db.query(Inspection).filter(Inspection.overall_status == "REVIEW_REQUIRED").count()
    pending = db.query(Inspection).filter(Inspection.overall_status == "PENDING").count()

    stats = DashboardStats(
        total_inspections=db.query(Inspection).count(),
        compliant=compliant,
        violations=violations,
        review_required=review_required,
        pending=pending,
    )

    recent = (
        db.query(Inspection)
        .order_by(
            Inspection.inspection_date.desc(),
            Inspection.created_at.desc(),
            Inspection.inspection_id.desc(),
        )
        .limit(recent_count)
        .all()
    )

    summaries = [
        _inspection_to_summary(insp, len(insp.violations), _review_decision(insp))
        for insp in recent
    ]

    return DashboardResponse(
        stats=stats,
        recent_inspections=summaries,
    )


@app.get(
    "/inspection/{inspection_id}/report",
    response_model=InspectionReport,
    tags=["Reports"],
    summary="Full inspection report",
    description="Returns the complete inspection report from PostgreSQL "
                "including declarations, checks, violations, evidence, "
                "AI analysis, and inspector decision.",
)
def get_inspection_report(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    insp = (
        db.query(Inspection)
        .filter(Inspection.inspection_id == inspection_id)
        .first()
    )
    if insp is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "inspection_not_found",
                "message": f"No inspection found with ID '{inspection_id}'",
            },
        )
    totals = {
        "declarations": len(insp.declarations),
        "violations": len(insp.violations),
        "reviews": len(insp.reviews),
    }
    return _inspection_to_report(insp, totals)
