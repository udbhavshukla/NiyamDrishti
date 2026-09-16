"""Resolve the currently applicable version from rule records, not code."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Rule


def get_current_rules(db: Session, as_of: datetime | None = None) -> tuple[str | None, list[Rule]]:
    """Return the active, effective rule version and its rules.

    The version is selected from the records supplied by the legal team.  This
    function deliberately contains no legal rule IDs, dates, or requirements.
    """
    as_of = (as_of or datetime.utcnow()).replace(tzinfo=None)
    candidates = (
        db.query(Rule)
        .filter(
            Rule.active.is_(True),
            or_(Rule.effective_from.is_(None), Rule.effective_from <= as_of),
            or_(Rule.effective_to.is_(None), Rule.effective_to >= as_of),
        )
        .order_by(Rule.effective_from.desc().nullslast(), Rule.id.desc())
        .all()
    )

    if not candidates:
        return None, []

    # The newest effective rule determines the active ruleset version.  All
    # checks then use only rules from that same version.
    version = candidates[0].version
    return version, [rule for rule in candidates if rule.version == version]
