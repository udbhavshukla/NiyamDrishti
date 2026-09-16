"""Regression tests for Member 3 backend bug fixes (SIH round 26034).

Covers:
  - BUG-002: e-commerce rule scoping (physical/e-commerce/unconfirmed)
  - BUG-003: corrupt/empty image uploads return HTTP 400
  - BUG-007: mutating endpoints require an authenticated officer token
  - BUG-009: CORS uses explicit origins (not wildcard + credentials)
  - AUTH_SECRET_KEY: fail-closed behaviour when the env var is missing
  - Evidence security: authenticated access + path traversal rejection
  - Multi-panel evidence: panel uploads merge instead of replacing prior data
"""

import io
import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("AUTH_SECRET_KEY", "test-key-for-sih-26034")

from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image

from app.database import create_tables
from app.main import app, get_evidence_file
from app.schemas import OCRField
from app.services.rule_engine import evaluate_rules
from app.auth import create_token, verify_token

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ECOM_RULE = SimpleNamespace(
    rule_id="LM-PC-006-10-ECOM-V1",
    field_name="ECOMMERCE_LISTING_DECLARATIONS",
    requirement_type="mandatory_declaration",
    requirement="Every e-commerce entity offering a pre-packaged commodity must display Rule 6(1) declarations.",
    severity="high",
    source_reference="Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 6(10)",
)

PHYSICAL_RULE = SimpleNamespace(
    rule_id="LM-PC-006-1C",
    field_name="NET_QUANTITY",
    requirement_type="mandatory_declaration",
    requirement="Net quantity must be declared in standard units.",
    severity="critical",
    source_reference="Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 6(1)(c)",
)

_TOKEN = None


def _token() -> str:
    global _TOKEN
    if _TOKEN is None:
        resp = TestClient(app).post(
            "/auth/login",
            json={"officer_id": "LMO-DEL-2024-884", "pin": "8842"},
        )
        _TOKEN = resp.json()["access_token"]
    return _TOKEN


def _auth() -> dict:
    return {"Authorization": f"Bearer {_token()}"}


def _make_image_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (300, 300), color=(200, 200, 200)).save(buf, format="JPEG")
    return buf.getvalue()


def _create_inspection(client: TestClient) -> str:
    resp = client.post(
        "/inspection",
        json={"product_name": "Regression Product", "inspector_id": "FSO-TST-001"},
        headers=_auth(),
    )
    assert resp.status_code == 201
    return resp.json()["inspection_id"]


# ---------------------------------------------------------------------------
# BUG-002 — E-commerce rule scoping (pure engine level)
# ---------------------------------------------------------------------------

class EcommerceScopingEngineTests(unittest.TestCase):
    def test_physical_context_marks_ecom_rule_not_applicable(self):
        result = evaluate_rules(
            {"net_quantity": OCRField(value="500 g", confidence=0.97)},
            [PHYSICAL_RULE, ECOM_RULE],
            "test",
            is_ecommerce=False,
        )
        self.assertEqual(result["overall_status"], "PASS")
        statuses = {check["rule_id"]: check["status"] for check in result["checks"]}
        self.assertEqual(statuses[ECOM_RULE.rule_id], "NOT_APPLICABLE")
        self.assertEqual(statuses[PHYSICAL_RULE.rule_id], "PASS")
        self.assertEqual(result["violations"], [])

    def test_unconfirmed_context_routes_ecom_rule_to_review(self):
        result = evaluate_rules(
            {"net_quantity": OCRField(value="500 g", confidence=0.97)},
            [PHYSICAL_RULE, ECOM_RULE],
            "test",
            is_ecommerce=None,
        )
        self.assertEqual(result["overall_status"], "REVIEW_REQUIRED")
        statuses = {check["rule_id"]: check["status"] for check in result["checks"]}
        self.assertEqual(statuses[ECOM_RULE.rule_id], "REVIEW_REQUIRED")

    def test_ecommerce_context_evaluates_ecom_rule(self):
        result = evaluate_rules(
            {"net_quantity": OCRField(value="500 g", confidence=0.97)},
            [PHYSICAL_RULE, ECOM_RULE],
            "test",
            is_ecommerce=True,
        )
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(
            any(v["rule_id"] == ECOM_RULE.rule_id for v in result["violations"])
        )

    def test_ecommerce_context_passes_when_declaration_present(self):
        result = evaluate_rules(
            {
                "net_quantity": OCRField(value="500 g", confidence=0.97),
                "ECOMMERCE_LISTING_DECLARATIONS": OCRField(value="Displayed fully", confidence=0.96),
            },
            [PHYSICAL_RULE, ECOM_RULE],
            "test",
            is_ecommerce=True,
        )
        self.assertEqual(result["overall_status"], "PASS")
        statuses = {check["rule_id"]: check["status"] for check in result["checks"]}
        self.assertEqual(statuses[ECOM_RULE.rule_id], "PASS")

    def test_default_absent_context_is_unconfirmed_not_fail(self):
        # No is_ecommerce argument provided → must never hard-FAIL on e-com rules.
        result = evaluate_rules(
            {"net_quantity": OCRField(value="500 g", confidence=0.97)},
            [PHYSICAL_RULE, ECOM_RULE],
            "test",
        )
        self.assertNotEqual(result["overall_status"], "FAIL")
        statuses = {check["rule_id"]: check["status"] for check in result["checks"]}
        self.assertIn(statuses[ECOM_RULE.rule_id], ("REVIEW_REQUIRED", "NOT_APPLICABLE"))


# ---------------------------------------------------------------------------
# BUG-007 — Authentication on mutating endpoints
# ---------------------------------------------------------------------------

class AuthGuardApiTests(unittest.TestCase):
    def setUp(self):
        create_tables()
        self.client = TestClient(app)

    def test_unauth_create_inspection_returns_401(self):
        resp = self.client.post("/inspection", json={"product_name": "X", "inspector_id": "Y"})
        self.assertEqual(resp.status_code, 401)

    def test_unauth_quick_scan_returns_401(self):
        img = _make_image_bytes()
        resp = self.client.post(
            "/inspection/quick-scan",
            files={"file": ("label.jpg", img, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 401)

    def test_unauth_analyze_returns_401(self):
        insp_id = _create_inspection(self.client)
        resp = self.client.post(f"/inspection/{insp_id}/analyze", json={})
        self.assertEqual(resp.status_code, 401)

    def test_unauth_evidence_returns_401(self):
        insp_id = _create_inspection(self.client)
        resp = self.client.post(
            f"/inspection/{insp_id}/evidence",
            files={"file": ("label.jpg", _make_image_bytes(), "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 401)

    def test_unauth_review_returns_401(self):
        insp_id = _create_inspection(self.client)
        resp = self.client.post(f"/inspection/{insp_id}/review", json={"decision": "PASS"})
        self.assertEqual(resp.status_code, 401)

    def test_authed_create_inspection_records_token_identity(self):
        resp = self.client.post(
            "/inspection",
            json={"product_name": "Token Identity", "inspector_id": "FSO-TST-001"},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertEqual(body["inspector_id"], "LMO-DEL-2024-884")
        self.assertIn("is_ecommerce", body)

    def test_authed_review_records_token_reviewer(self):
        insp_id = _create_inspection(self.client)
        resp = self.client.post(f"/inspection/{insp_id}/review", json={"decision": "PASS"}, headers=_auth())
        self.assertEqual(resp.status_code, 200)
        detail = self.client.get(f"/inspection/{insp_id}").json()
        self.assertEqual(detail["reviews"][0]["reviewer_id"], "LMO-DEL-2024-884")


# ---------------------------------------------------------------------------
# BUG-003 — Corrupt / empty / non-image uploads → HTTP 400
# ---------------------------------------------------------------------------

class InvalidImageUploadTests(unittest.TestCase):
    def setUp(self):
        create_tables()
        self.client = TestClient(app)

    def _dashboard_total(self) -> int:
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)
        return resp.json()["stats"]["total_inspections"]

    def test_quick_scan_corrupt_file_returns_400(self):
        before = self._dashboard_total()
        resp = self.client.post(
            "/inspection/quick-scan",
            files={"file": ("requirements.txt", "not an image".encode(), "text/plain")},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("invalid_image_file", resp.json()["detail"].get("error", ""))
        self.assertEqual(self._dashboard_total(), before, "no orphan PENDING inspection should remain")

    def test_quick_scan_empty_file_returns_400(self):
        resp = self.client.post(
            "/inspection/quick-scan",
            files={"file": ("empty.jpg", b"", "image/jpeg")},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 400)

    def test_evidence_corrupt_file_returns_400(self):
        insp_id = _create_inspection(self.client)
        resp = self.client.post(
            f"/inspection/{insp_id}/evidence",
            files={"file": ("corrupt.jpg", b"not an image", "image/jpeg")},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 400)

    def test_evidence_non_image_mime_returns_400(self):
        insp_id = _create_inspection(self.client)
        resp = self.client.post(
            f"/inspection/{insp_id}/evidence",
            files={"file": ("notes.txt", _make_image_bytes(), "text/plain")},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["detail"]["error"], "invalid_image_file")

    def test_valid_image_still_returns_200(self):
        insp_id = _create_inspection(self.client)
        resp = self.client.post(
            f"/inspection/{insp_id}/evidence",
            files={"file": ("label.jpg", _make_image_bytes(), "image/jpeg")},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# BUG-009 — CORS explicit origins
# ---------------------------------------------------------------------------

class CorsConfigTests(unittest.TestCase):
    def setUp(self):
        create_tables()
        self.client = TestClient(app)

    def test_preflight_returns_explicit_origin_not_wildcard(self):
        resp = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertIn("access-control-allow-origin", resp.headers)
        self.assertEqual(resp.headers["access-control-allow-origin"], "http://localhost:5173")
        self.assertEqual(resp.headers["access-control-allow-credentials"], "true")

    def test_disallowed_origin_is_not_echoed(self):
        resp = self.client.options(
            "/health",
            headers={
                "Origin": "http://evil.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertNotIn("access-control-allow-origin", resp.headers)


# ---------------------------------------------------------------------------
# AUTH_SECRET_KEY — fail closed when env var missing
# ---------------------------------------------------------------------------

class SecretKeyFailClosedTests(unittest.TestCase):
    def test_missing_secret_key_fails_closed(self):
        old = os.environ.get("AUTH_SECRET_KEY")
        os.environ.pop("AUTH_SECRET_KEY", None)
        try:
            self.assertIsNone(verify_token("anything"))
            with self.assertRaises(HTTPException) as ctx:
                create_token("LMO-DEL-2024-884")
            self.assertEqual(ctx.exception.status_code, 500)
            resp = TestClient(app).post(
                "/auth/login",
                json={"officer_id": "LMO-DEL-2024-884", "pin": "8842"},
            )
            self.assertEqual(resp.status_code, 500)
        finally:
            if old is not None:
                os.environ["AUTH_SECRET_KEY"] = old
            else:
                os.environ.pop("AUTH_SECRET_KEY", None)


# ---------------------------------------------------------------------------
# Evidence security — authenticated access + traversal protection
# ---------------------------------------------------------------------------

class EvidenceSecurityTests(unittest.TestCase):
    def setUp(self):
        create_tables()
        self.client = TestClient(app)

    def _upload_and_get_url(self) -> str:
        insp_id = _create_inspection(self.client)
        resp = self.client.post(
            f"/inspection/{insp_id}/evidence",
            files={"file": ("label.jpg", _make_image_bytes(), "image/jpeg")},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 200)
        return insp_id, resp.json()["evidence_url"]

    def test_evidence_requires_auth(self):
        _, evidence_url = self._upload_and_get_url()
        resp = self.client.get(evidence_url)
        self.assertEqual(resp.status_code, 401)

    def test_evidence_served_with_bearer_header(self):
        _, evidence_url = self._upload_and_get_url()
        resp = self.client.get(evidence_url, headers=_auth())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["content-type"].split(";")[0], "image/jpeg")

    def test_evidence_served_with_token_query_param(self):
        _, evidence_url = self._upload_and_get_url()
        resp = self.client.get(f"{evidence_url}?token={_token()}")
        self.assertEqual(resp.status_code, 200)

    def test_evidence_path_traversal_is_rejected(self):
        auth_header = f"Bearer {_token()}"
        # Directly exercise the security checks with an invalid inspection id.
        with self.assertRaises(HTTPException) as ctx:
            get_evidence_file("..", "x.jpg", authorization=auth_header)
        self.assertEqual(ctx.exception.status_code, 400)

        # A ".." filename resolves inside the root but is not a file → 404.
        with self.assertRaises(HTTPException) as ctx:
            get_evidence_file("INS-REGRESSION-001", "..", authorization=auth_header)
        self.assertEqual(ctx.exception.status_code, 404)

        # A nonexistent file under a valid inspection → 404.
        with self.assertRaises(HTTPException) as ctx:
            get_evidence_file("INS-REGRESSION-001", "primary_1234567890_aaaaaaaa.jpg", authorization=auth_header)
        self.assertEqual(ctx.exception.status_code, 404)


# ---------------------------------------------------------------------------
# Multi-panel evidence accumulation
# ---------------------------------------------------------------------------

class MultiPanelEvidenceTests(unittest.TestCase):
    def setUp(self):
        create_tables()
        self.client = TestClient(app)

    def test_evidence_panel_merges_instead_of_replacing(self):
        insp_id = _create_inspection(self.client)

        # Panel A: structured facts supplied via /analyze (simulates a scan).
        resp = self.client.post(
            f"/inspection/{insp_id}/analyze",
            json={
                "manufacturing_date": {"value": "2026-05", "confidence": 0.98},
                "NET_QUANTITY": {"value": "500 g", "confidence": 0.97},
                "custom_trace_field": {"value": "kept-after-merge", "confidence": 0.99},
            },
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 200)

        # Panel B: image evidence upload (simulates a different label panel).
        resp = self.client.post(
            f"/inspection/{insp_id}/evidence",
            files={"file": ("mrp_panel.jpg", _make_image_bytes(), "image/jpeg")},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(
            f"/inspection/{insp_id}/evidence",
            files={"file": ("manufacturer_panel.jpg", _make_image_bytes(), "image/jpeg")},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 200)

        detail = self.client.get(f"/inspection/{insp_id}").json()
        declarations = detail["declarations"]
        fields = [d["field_name"] for d in declarations]

        # Prior scan fields are preserved (no destructive replacement).
        self.assertIn("custom_trace_field", fields)
        self.assertIn("manufacturing_date", fields)
        self.assertIn("NET_QUANTITY", fields)

        # OCR panels produced their normal fields too.
        self.assertIn("mrp", fields)
        self.assertIn("net_quantity", fields)

        # No duplicate field rows after two panel uploads.
        self.assertEqual(len(fields), len(set(fields)))


if __name__ == "__main__":
    unittest.main()