"""Minimal inspector-review tests."""

from unittest import TestCase

from pydantic import ValidationError

from app.database import SessionLocal, create_tables
from app.main import create_inspection, review_inspection
from app.models import Inspection, Review
from app.schemas import CreateInspectionRequest, ReviewInspectionRequest


class ReviewRequestTests(TestCase):
    def test_accepts_pass_fail_or_review_required(self):
        for decision in ("PASS", "FAIL", "REVIEW_REQUIRED"):
            body = ReviewInspectionRequest(decision=decision)
            self.assertEqual(body.decision, decision)

    def test_rejects_unknown_decision(self):
        with self.assertRaises(ValidationError):
            ReviewInspectionRequest(decision="approved")


class ReviewPersistenceTests(TestCase):
    def test_review_is_saved_and_status_updated(self):
        create_tables()
        db = SessionLocal()
        try:
            created = create_inspection(
                CreateInspectionRequest(product_name="ABC Detergent", inspector_id="FSO-MH-001"),
                db,
            )
            inspection_id = created["inspection_id"]
            result = review_inspection(
                inspection_id,
                ReviewInspectionRequest(
                    decision="PASS",
                    comment="Label complete",
                    reviewer_id="FSO-MH-001",
                ),
                db,
            )
            self.assertEqual(result["overall_status"], "PASS")
            self.assertEqual(result["review"]["decision"], "PASS")
            self.assertEqual(result["review"]["comment"], "Label complete")
            self.assertEqual(result["review"]["reviewer_id"], "FSO-MH-001")

            inspection = db.query(Inspection).filter(Inspection.inspection_id == inspection_id).one()
            reviews = db.query(Review).filter(Review.inspection_id == inspection_id).all()
            self.assertEqual(inspection.overall_status, "PASS")
            self.assertEqual(len(reviews), 1)
            self.assertEqual(reviews[0].decision, "PASS")
        finally:
            db.close()
