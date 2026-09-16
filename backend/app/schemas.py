"""
Pydantic models (schemas) for the NiyamDrishti API.

These models define the request/response shapes for all Phase 7 endpoints.
Designed to be easy to consume from React (fetch/axios) and Flutter (Dio/http).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, RootModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class InspectionStatus(str, Enum):
    COMPLIANT = "compliant"
    VIOLATION = "violation"
    REVIEW_REQUIRED = "review_required"
    PENDING = "pending"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CheckResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"


class InspectorDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    PENDING_REVIEW = "pending_review"


# ---------------------------------------------------------------------------
# Sub-models used inside Inspection / Report
# ---------------------------------------------------------------------------

class Declaration(BaseModel):
    """A single declaration made on the product label / documentation."""
    id: str
    field_name: str = Field(..., description="e.g. 'ingredients', 'net_weight', 'manufacturer'")
    declared_value: str
    verified: bool
    notes: Optional[str] = None


class ComplianceCheck(BaseModel):
    """One compliance check performed during the inspection."""
    id: str
    rule_code: str = Field(..., description="Reference to the regulatory rule, e.g. 'FSSAI-2.1.3'")
    description: str
    result: CheckResult
    details: Optional[str] = None


class Violation(BaseModel):
    """A violation found during inspection."""
    id: str
    rule_code: str
    description: str
    severity: Severity
    recommended_action: Optional[str] = None


class Evidence(BaseModel):
    """Evidence collected during the inspection (photo, document, etc.)."""
    id: str
    type: str = Field(..., description="e.g. 'photo', 'document', 'lab_report'")
    url: str = Field(..., description="URL or path to the evidence file")
    description: Optional[str] = None
    captured_at: Optional[datetime] = None


class AIAnalysis(BaseModel):
    """AI-generated analysis results."""
    model_config = {"protected_namespaces": ()}

    confidence_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall AI confidence (0.0 = no confidence, 1.0 = full confidence)"
    )
    model_version: str = Field(..., description="AI model version used for analysis")
    findings: list[str] = Field(default_factory=list, description="Key AI findings")
    suggested_status: InspectionStatus = Field(..., description="AI-suggested compliance status")


class ProductInfo(BaseModel):
    """Product being inspected."""
    id: str
    name: str
    category: str
    brand: Optional[str] = None
    batch_number: Optional[str] = None
    barcode: Optional[str] = None


class InspectorInfo(BaseModel):
    """Inspector who performed the inspection."""
    id: str
    name: str
    badge_number: Optional[str] = None
    department: Optional[str] = None


# ---------------------------------------------------------------------------
# Inspection list item (lightweight, used in GET /inspections)
# ---------------------------------------------------------------------------

class InspectionSummary(BaseModel):
    """Lightweight inspection record returned in list views."""
    id: str
    product: ProductInfo
    inspector: InspectorInfo
    status: InspectionStatus
    date: datetime
    ai_confidence: float = Field(..., ge=0.0, le=1.0)
    violation_count: int = Field(..., ge=0)
    inspector_decision: InspectorDecision


# ---------------------------------------------------------------------------
# Full inspection report (GET /inspection/{inspection_id}/report)
# ---------------------------------------------------------------------------

class InspectionReport(BaseModel):
    """Complete inspection report with all details."""
    inspection_id: str
    product: ProductInfo
    inspector: InspectorInfo
    date: datetime
    rule_version: str = Field(..., description="Version of the ruleset used, e.g. 'FSSAI-v2.3'")
    status: InspectionStatus

    # Detailed sections
    declarations: list[Declaration] = Field(default_factory=list)
    checks: list[ComplianceCheck] = Field(default_factory=list)
    violations: list[Violation] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)

    # AI analysis
    ai_analysis: AIAnalysis

    # Human decision
    inspector_decision: InspectorDecision
    inspector_remarks: Optional[str] = None


# ---------------------------------------------------------------------------
# Dashboard (GET /dashboard)
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    """Aggregate statistics for the dashboard."""
    total_inspections: int
    compliant: int
    violations: int
    review_required: int
    pending: int


class DashboardResponse(BaseModel):
    """Full dashboard payload."""
    stats: DashboardStats
    recent_inspections: list[InspectionSummary] = Field(
        default_factory=list,
        description="Most recent inspections (default: last 10)"
    )


# ---------------------------------------------------------------------------
# List endpoint wrapper (GET /inspections)
# ---------------------------------------------------------------------------

class InspectionListResponse(BaseModel):
    """Paginated list of inspections."""
    total: int
    page: int
    page_size: int
    inspections: list[InspectionSummary]


# ---------------------------------------------------------------------------
# Phase 2: Inspection CRUD schemas (flat, matching DB models)
# ---------------------------------------------------------------------------

class CreateInspectionRequest(BaseModel):
    """
    Request body for POST /inspection.

    Frontend/Flutter sends this to create a new inspection.
    Only product_name and inspector_id are required.
    """
    product_name: str = Field(..., description="Name of the product being inspected")
    inspector_id: str = Field(..., description="ID of the inspector performing the inspection")
    is_ecommerce: Optional[bool] = Field(
        default=None,
        description="True = e-commerce digital listing; False = physical retail package; None = unconfirmed.",
    )


class DeclarationOut(BaseModel):
    """One OCR-extracted field, as stored in the DB."""
    id: int
    field_name: str
    value: Optional[str] = None
    confidence: Optional[float] = None
    bbox: Optional[str] = None
    source: Optional[str] = "ocr"


class ViolationOut(BaseModel):
    """One violation, as stored in the DB."""
    id: int
    rule_id: str
    field_name: Optional[str] = None
    severity: str = "medium"
    status: str = "open"
    reason: Optional[str] = None
    evidence_image: Optional[str] = None
    bbox: Optional[str] = None
    extracted_text: Optional[str] = None
    confidence: Optional[float] = None


class ReviewOut(BaseModel):
    """One inspector review, as stored in the DB."""
    id: int
    decision: str
    comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[str] = None


class InspectionDetail(BaseModel):
    """
    Full inspection record from the database.

    Returned by GET /inspection/{inspection_id}.
    Includes related declarations, violations, and reviews.
    """
    inspection_id: str
    product_name: str
    inspector_id: str
    inspection_date: Optional[datetime] = None
    rule_version: Optional[str] = None
    overall_status: str = "PENDING"
    confidence: Optional[float] = None
    is_ecommerce: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    declarations: list[DeclarationOut] = Field(default_factory=list)
    violations: list[ViolationOut] = Field(default_factory=list)
    reviews: list[ReviewOut] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Sprint 1: OCR integration, rule repository, and deterministic analysis
# ---------------------------------------------------------------------------

class OCRField(BaseModel):
    """One fact extracted by Member 1's OCR/AI pipeline.

    Confidence is an AI-quality signal only.  It is never a legal threshold.
    ``evidence_image`` is optional metadata pointing to the source image/crop.
    """
    value: str | int | float | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    bbox: list[float] | None = None
    source: str = "ocr"
    evidence_image: str | None = None


class OCRDeclarationsPayload(RootModel[dict[str, OCRField]]):
    """The direct JSON mapping sent by the OCR service (field name → fact)."""


class RuleOut(BaseModel):
    id: int
    rule_id: str
    version: str
    field_name: str
    requirement_type: str
    requirement: str
    severity: str
    explanation: str | None = None
    source_reference: str | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    active: bool


class CurrentRulesResponse(BaseModel):
    rule_version: str | None = None
    rules: list[RuleOut] = Field(default_factory=list)
    warning: str | None = None


class AnalysisCheck(BaseModel):
    rule_id: str
    field: str
    status: str = Field(pattern="^(PASS|FAIL|REVIEW_REQUIRED|NOT_APPLICABLE)$")
    value: str | None = None
    confidence: float | None = None
    reason: str


class AnalysisViolation(BaseModel):
    id: int
    rule_id: str
    field_name: str | None = None
    severity: str
    status: str
    reason: str | None = None
    evidence_image: str | None = None
    bbox: str | None = None
    extracted_text: str | None = None
    confidence: float | None = None


class AnalyzeInspectionResponse(BaseModel):
    inspection_id: str
    overall_status: str = Field(pattern="^(PASS|FAIL|REVIEW_REQUIRED)$")
    rule_version: str | None = None
    confidence: float | None = None
    is_ecommerce: bool | None = None
    checks: list[AnalysisCheck] = Field(default_factory=list)
    violations: list[AnalysisViolation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ReviewInspectionRequest(BaseModel):
    """Inspector override/confirmation after machine analysis."""
    decision: str = Field(pattern="^(PASS|FAIL|REVIEW_REQUIRED)$")
    comment: str | None = None
    reviewer_id: str | None = None


class ReviewInspectionResponse(BaseModel):
    inspection_id: str
    overall_status: str = Field(pattern="^(PASS|FAIL|REVIEW_REQUIRED)$")
    review: ReviewOut
