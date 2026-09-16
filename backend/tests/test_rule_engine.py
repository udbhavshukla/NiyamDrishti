"""Focused deterministic rule-engine tests; no database or legal data needed."""

from types import SimpleNamespace
import unittest

from app.schemas import OCRField
from app.services.rule_engine import evaluate_rules


TEST_REQUIRED_RULE = SimpleNamespace(
    rule_id="TEST-REQUIRED",
    field_name="product_name",
    requirement_type="required",
    requirement="present",
    severity="medium",
)

VERIFIED_REQUIRED_RULE = SimpleNamespace(
    **TEST_REQUIRED_RULE.__dict__,
    source_reference="Member 2 import — verified legal source already stored",
)


class RuleEngineTests(unittest.TestCase):
    """Synthetic fixtures verify engine behavior, not legal requirements."""

    def test_high_confidence_present_required_field_passes(self):
        result = evaluate_rules(
            {"product_name": OCRField(value="ABC Detergent", confidence=0.97)},
            [VERIFIED_REQUIRED_RULE],
            "test",
        )
        self.assertEqual(result["overall_status"], "PASS")
        self.assertEqual(result["checks"][0]["status"], "PASS")

    def test_missing_required_field_fails(self):
        result = evaluate_rules({}, [VERIFIED_REQUIRED_RULE], "test")
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertEqual(result["violations"][0]["rule_id"], "TEST-REQUIRED")

    def test_low_confidence_routes_to_human_review(self):
        result = evaluate_rules(
            {"product_name": OCRField(value="ABC Detergent", confidence=0.55)},
            [VERIFIED_REQUIRED_RULE],
            "test",
        )
        self.assertEqual(result["overall_status"], "REVIEW_REQUIRED")
        self.assertEqual(result["violations"], [])

    def test_unverified_rule_does_not_pass_or_fail(self):
        result = evaluate_rules(
            {"product_name": OCRField(value="ABC Detergent", confidence=0.97)},
            [TEST_REQUIRED_RULE],
            "test",
        )
        self.assertEqual(result["overall_status"], "REVIEW_REQUIRED")
        self.assertEqual(result["checks"][0]["status"], "REVIEW_REQUIRED")
        self.assertIn("LEGAL SOURCE VERIFICATION REQUIRED", result["checks"][0]["reason"])
        self.assertEqual(result["violations"], [])

    def test_no_rules_emits_per_field_review(self):
        result = evaluate_rules(
            {"mrp": OCRField(value="₹120", confidence=0.95)},
            [],
            None,
        )
        self.assertEqual(result["overall_status"], "REVIEW_REQUIRED")
        self.assertEqual(result["checks"][0]["rule_id"], "UNVERIFIED")
        self.assertEqual(result["checks"][0]["field"], "mrp")
        self.assertEqual(result["checks"][0]["value"], "₹120")
        self.assertEqual(result["checks"][0]["confidence"], 0.95)
        self.assertEqual(result["checks"][0]["reason"], "LEGAL SOURCE VERIFICATION REQUIRED")


if __name__ == "__main__":
    unittest.main()
