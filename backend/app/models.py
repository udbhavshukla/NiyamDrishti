"""
SQLAlchemy ORM models for NiyamDrishti.

Five tables matching the project spec:
  - inspections  : the core inspection record
  - declarations : OCR-extracted fields from product labels
  - violations   : compliance failures found by the rule engine
  - reviews      : inspector decisions (human-in-the-loop)
  - rules        : versioned legal/regulatory rules

Each model is intentionally simple — easy to explain to SIH judges.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


# ──────────────────────────────────────────────────────────────────────────────
# INSPECTIONS
# ──────────────────────────────────────────────────────────────────────────────

class Inspection(Base):
    """
    Core inspection record.

    One inspection = one product checked against one version of the rules.
    """
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_id = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    inspector_id = Column(String(50), nullable=False)
    inspection_date = Column(DateTime, default=_utcnow)
    rule_version = Column(String(20), nullable=True)

    # Overall result: PASS / FAIL / REVIEW_REQUIRED / PENDING
    overall_status = Column(String(30), default="PENDING")

    # Inspection context: False = physical retail commodity, True = e-commerce digital listing, None = unconfirmed
    is_ecommerce = Column(Boolean, default=False, nullable=True)

    # AI confidence (average or overall)
    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    declarations = relationship("Declaration", back_populates="inspection", cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="inspection", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="inspection", cascade="all, delete-orphan")


# ──────────────────────────────────────────────────────────────────────────────
# DECLARATIONS  (OCR-extracted fields from product labels)
# ──────────────────────────────────────────────────────────────────────────────

class Declaration(Base):
    """
    One field extracted from a product label by OCR/AI.

    Example: field_name="mrp", value="₹120", confidence=0.95
    """
    __tablename__ = "declarations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_id = Column(String(50), ForeignKey("inspections.inspection_id"), nullable=False, index=True)

    field_name = Column(String(100), nullable=False)   # e.g. "product_name", "mrp", "net_weight"
    value = Column(Text, nullable=True)                # extracted text
    confidence = Column(Float, nullable=True)          # OCR confidence 0.0-1.0
    bbox = Column(Text, nullable=True)                 # JSON string: [x1, y1, x2, y2]
    source = Column(String(50), default="ocr")         # "ocr", "manual", "ai"

    inspection = relationship("Inspection", back_populates="declarations")


# ──────────────────────────────────────────────────────────────────────────────
# VIOLATIONS  (compliance failures)
# ──────────────────────────────────────────────────────────────────────────────

class Violation(Base):
    """
    A compliance violation found by the rule engine.

    Links an inspection to a specific rule that was broken.
    """
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_id = Column(String(50), ForeignKey("inspections.inspection_id"), nullable=False, index=True)

    rule_id = Column(String(50), nullable=False)       # which rule was violated
    field_name = Column(String(100), nullable=True)    # which label field
    severity = Column(String(20), default="medium")    # low / medium / high / critical
    status = Column(String(20), default="open")        # open / resolved / dismissed
    reason = Column(Text, nullable=True)               # human-readable explanation

    # Evidence linking
    evidence_image = Column(Text, nullable=True)       # path to image crop
    bbox = Column(Text, nullable=True)                 # bounding box on original image
    extracted_text = Column(Text, nullable=True)       # what AI actually read
    confidence = Column(Float, nullable=True)          # AI confidence for this field

    inspection = relationship("Inspection", back_populates="violations")


# ──────────────────────────────────────────────────────────────────────────────
# REVIEWS  (inspector decisions — human-in-the-loop)
# ──────────────────────────────────────────────────────────────────────────────

class Review(Base):
    """
    Inspector's decision on an inspection.

    The system recommends → the inspector confirms or overrides.
    """
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_id = Column(String(50), ForeignKey("inspections.inspection_id"), nullable=False, index=True)

    decision = Column(String(30), nullable=False)      # approved / rejected / escalated
    comment = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=_utcnow)
    reviewer_id = Column(String(50), nullable=True)

    inspection = relationship("Inspection", back_populates="reviews")


# ──────────────────────────────────────────────────────────────────────────────
# RULES  (versioned regulatory requirements)
# ──────────────────────────────────────────────────────────────────────────────

class Rule(Base):
    """
    One regulatory rule/requirement.

    Rules are versioned — old inspections can still be explained
    using the rule version they were checked against.

    IMPORTANT: Rule content comes from Member 2 (Legal).
    Rules marked with unverified source_reference need
    LEGAL SOURCE VERIFICATION REQUIRED.
    """
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(String(50), nullable=False, index=True)   # e.g. "PC-001"
    version = Column(String(20), nullable=False)                # e.g. "2026.1"

    field_name = Column(String(100), nullable=False)            # which label field this rule checks
    requirement_type = Column(String(50), nullable=False)       # "required", "format", "range", "pattern"
    requirement = Column(Text, nullable=False)                  # the actual rule logic/description
    severity = Column(String(20), default="medium")             # low / medium / high / critical
    explanation = Column(Text, nullable=True)                   # judge-friendly explanation

    source_reference = Column(Text, nullable=True)              # legal source
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
