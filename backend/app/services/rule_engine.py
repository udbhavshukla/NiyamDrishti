"""Small deterministic rule engine for already-verified database rules.

OCR/AI supplies facts and confidence.  This module evaluates those facts using
only the rule records selected by the version resolver; it never creates legal
requirements or asks an LLM to make a compliance decision.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping


HIGH_CONFIDENCE = 0.90
REVIEW_CONFIDENCE = 0.60
UNVERIFIED_RULE_ID = "UNVERIFIED"
LEGAL_SOURCE_REQUIRED = "LEGAL SOURCE VERIFICATION REQUIRED"

# Rules whose field belongs to the digital marketplace listing (Rule 6(10)/6(10A))
# scope. They only apply when the inspection context is explicitly e-commerce.
ECOMMERCE_FIELD_PREFIX = "ECOMMERCE_"


def _value_is_present(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _check_confidence(confidence: float | None) -> str | None:
    """Return a review reason when OCR confidence is not decision-grade."""
    if confidence is None:
        return "OCR confidence was not supplied; inspector review is required."
    if confidence < REVIEW_CONFIDENCE:
        return "OCR confidence is below 0.60; inspector review is required."
    if confidence < HIGH_CONFIDENCE:
        return "OCR confidence is in the 0.60–0.89 review zone."
    return None


FIELD_ALIASES: dict[str, list[str]] = {
    "COMMODITY_COMMON_OR_GENERIC_NAME": ["product_name", "commodity_name", "generic_name", "product"],
    "NET_QUANTITY": ["net_quantity", "net_qty", "net_weight", "net_volume", "quantity"],
    "MRP_RETAIL_SALE_PRICE": ["mrp", "retail_sale_price", "maximum_retail_price", "price"],
    "MANUFACTURER_PACKER_IMPORTER_NAME_ADDRESS": [
        "manufacturer", "address", "manufacturer_address", "packer", "importer", "manufacturer_name_and_address"
    ],
    "MONTH_YEAR_OF_MANUFACTURE_PACKING_IMPORT": [
        "manufacturing_date", "mfg_date", "date_of_manufacture", "pkd_date", "packed_date", "date"
    ],
    "CONSUMER_CARE_DETAILS": [
        "consumer_care", "customer_care", "helpline", "consumer_cell", "grievance", "consumer_care_details"
    ],
    "COUNTRY_OF_ORIGIN_IMPORTED_GOODS": [
        "country_of_origin", "coo", "origin", "made_in"
    ],
}


def get_declaration_for_rule(declarations: Mapping[str, Any], rule_field_name: str) -> Any:
    """Finds matching declaration fact using exact name, case-insensitivity, or aliases."""
    if rule_field_name in declarations:
        return declarations[rule_field_name]

    # Case-insensitive direct check
    for key, val in declarations.items():
        if key.casefold() == rule_field_name.casefold():
            return val

    # Alias check
    aliases = FIELD_ALIASES.get(rule_field_name, [])
    for alias in aliases:
        for key, val in declarations.items():
            if key.casefold() == alias.casefold():
                return val

    # Reverse alias check (if rule_field_name itself is an alias)
    for canonical_field, alias_list in FIELD_ALIASES.items():
        if rule_field_name.casefold() in [a.casefold() for a in alias_list]:
            if canonical_field in declarations:
                return declarations[canonical_field]
            for alias in alias_list:
                for key, val in declarations.items():
                    if key.casefold() == alias.casefold():
                        return val

    return None


def _evaluate_requirement(rule: Any, value: Any) -> tuple[str, str]:
    """Evaluate regulatory requirement types without subjective legal assumptions."""
    requirement_type = rule.requirement_type.lower().strip()
    text_value = "" if value is None else str(value).strip()

    if requirement_type in ("required", "mandatory_declaration"):
        if _value_is_present(value):
            return "PASS", "Mandatory statutory declaration is present on the package label."
        return "FAIL", "Mandatory statutory declaration is missing from the package label (Rule 6 contravention)."

    if requirement_type == "pattern":
        try:
            matches = re.fullmatch(rule.requirement, text_value) is not None
        except re.error:
            return "REVIEW_REQUIRED", "Stored rule pattern is invalid; inspector review is required."
        if matches:
            return "PASS", "Declaration matches the verified rule pattern."
        return "FAIL", "Declaration does not match the verified rule pattern."

    if requirement_type == "equals":
        if text_value.casefold() == rule.requirement.strip().casefold():
            return "PASS", "Declaration matches the verified rule value."
        return "FAIL", "Declaration does not match the verified rule value."

    if requirement_type == "prohibition":
        return (
            "REVIEW_REQUIRED",
            "Physical label check required: verify no sticker alters declarations or obscures MRP (Rule 6(3)).",
        )

    if requirement_type == "format_requirement":
        return (
            "REVIEW_REQUIRED",
            "Physical measurement check: verify numeral height matches Table 1 and language in Hindi/English (Rule 7/9).",
        )

    if requirement_type in ("conditional_exemption", "scope_limit"):
        return (
            "PASS",
            f"Statutory provision noted ({rule.requirement_type}): verified within inspection scope.",
        )

    return (
        "REVIEW_REQUIRED",
        f"Requirement type '{rule.requirement_type}' is not supported by the MVP engine.",
    )


def _is_legally_verified(rule: Any) -> bool:
    """A stored rule is usable only when a legal source reference is present."""
    reference = getattr(rule, "source_reference", None)
    if reference is None:
        return False
    text = str(reference).strip()
    if not text:
        return False
    return LEGAL_SOURCE_REQUIRED not in text.upper()


def _declaration_check(
    rule_id: str,
    field_name: str,
    declaration: Any,
    status: str,
    reason: str,
) -> dict[str, Any]:
    value = declaration.value if declaration is not None else None
    confidence = declaration.confidence if declaration is not None else None
    return {
        "rule_id": rule_id,
        "field": field_name,
        "status": status,
        "value": None if value is None else str(value),
        "confidence": confidence,
        "reason": reason,
    }


def evaluate_rules(
    declarations: Mapping[str, Any],
    rules: Iterable[Any],
    rule_version: str | None,
    is_ecommerce: bool | None = None,
) -> dict[str, Any]:
    """Evaluate declarations against one already-resolved rule version.

    Supported stored requirement types are ``required``, ``pattern``, and
    ``equals``.  Any unsupported configuration is routed to a human reviewer,
    never silently passed or failed.

    ``is_ecommerce`` controls scope for digital-listing rules (identified by
    their ``ECOMMERCE_*`` field).  A physical scan (``is_ecommerce=False``)
    reports them as ``NOT_APPLICABLE``; an unconfirmed context
    (``is_ecommerce=None``) routes them to ``REVIEW_REQUIRED``.
    """
    rules = list(rules)
    verified_rules = [rule for rule in rules if _is_legally_verified(rule)]
    unverified_rules = [rule for rule in rules if not _is_legally_verified(rule)]

    if not verified_rules:
        checks = [
            _declaration_check(
                getattr(rule, "rule_id", UNVERIFIED_RULE_ID),
                rule.field_name,
                declarations.get(rule.field_name),
                "REVIEW_REQUIRED",
                LEGAL_SOURCE_REQUIRED,
            )
            for rule in unverified_rules
        ]
        if not checks:
            checks = [
                _declaration_check(
                    UNVERIFIED_RULE_ID,
                    field_name,
                    declaration,
                    "REVIEW_REQUIRED",
                    LEGAL_SOURCE_REQUIRED,
                )
                for field_name, declaration in declarations.items()
            ]
        return {
            "overall_status": "REVIEW_REQUIRED",
            "rule_version": rule_version,
            "checks": checks,
            "violations": [],
            "warnings": [
                "No active, legally verified rules are available for evaluation. "
                + LEGAL_SOURCE_REQUIRED
            ],
        }

    checks: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []

    for rule in unverified_rules:
        checks.append(
            _declaration_check(
                rule.rule_id,
                rule.field_name,
                declarations.get(rule.field_name),
                "REVIEW_REQUIRED",
                LEGAL_SOURCE_REQUIRED,
            )
        )

    for rule in verified_rules:
        declaration = get_declaration_for_rule(declarations, rule.field_name)
        value = declaration.value if declaration is not None else None
        confidence = declaration.confidence if declaration is not None else None

        # --- E-commerce scoping ---------------------------------------------------
        # Rules whose canonical field starts with ECOMMERCE_ only apply to digital
        # marketplace listings, never to physical retail-package inspections.
        is_ecommerce_rule = getattr(rule, "field_name", "").upper().startswith(ECOMMERCE_FIELD_PREFIX)
        if is_ecommerce_rule:
            if is_ecommerce is False:
                check = _declaration_check(
                    rule.rule_id,
                    rule.field_name,
                    declaration,
                    "NOT_APPLICABLE",
                    "E-commerce listing requirement; not applicable to physical package labels.",
                )
                checks.append(check)
                continue
            if is_ecommerce is None:
                check = _declaration_check(
                    rule.rule_id,
                    rule.field_name,
                    declaration,
                    "REVIEW_REQUIRED",
                    "E-commerce listing requirement; inspection context (physical or e-commerce) is unconfirmed.",
                )
                checks.append(check)
                continue
            # is_ecommerce is True → fall through and evaluate normally

        req_type = rule.requirement_type.lower().strip()
        # A missing declaration is evaluated by verified required or mandatory_declaration rules.
        # For other rule types (e.g. format, prohibition), absence is ambiguous and belongs with a human.
        if declaration is None and req_type not in ("required", "mandatory_declaration"):
            status = "REVIEW_REQUIRED"
            reason = "Declaration is absent; inspector review is required."
        elif declaration is not None and (confidence_reason := _check_confidence(confidence)):
            status = "REVIEW_REQUIRED"
            reason = confidence_reason
        else:
            status, reason = _evaluate_requirement(rule, value)

        check = _declaration_check(rule.rule_id, rule.field_name, declaration, status, reason)
        checks.append(check)

        if status == "FAIL":
            violations.append(
                {
                    "rule_id": rule.rule_id,
                    "field": rule.field_name,
                    "severity": rule.severity,
                    "reason": reason,
                    "value": None if value is None else str(value),
                    "confidence": confidence,
                }
            )

    statuses = {check["status"] for check in checks}
    overall_status = (
        "FAIL"
        if "FAIL" in statuses
        else "REVIEW_REQUIRED"
        if "REVIEW_REQUIRED" in statuses
        else "PASS"
    )
    return {
        "overall_status": overall_status,
        "rule_version": rule_version,
        "checks": checks,
        "violations": violations,
        "warnings": [],
    }
