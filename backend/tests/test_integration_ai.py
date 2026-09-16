"""
End-to-end and integration tests for AI/OCR, Auth, and Evidence processing in NiyamDrishti.
"""

import io
import os
import unittest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

os.environ.setdefault("AUTH_SECRET_KEY", "test-key-for-sih-26034")

from app.auth import LoginRequest, authenticate_officer, create_token, verify_token
from app.database import create_tables
from app.main import app
from app.services.ai_ocr import (
    check_image_quality,
    extract_dates_with_separation,
    _find_closest_context_match,
    MRP_KEYWORDS,
    MRP_VALUE_PATTERN,
    NET_QTY_KEYWORDS,
    QUANTITY_VALUE_PATTERN,
    analyze_package_label,
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


class AuthTests(unittest.TestCase):
    def test_valid_officer_login(self):
        req = LoginRequest(officer_id="LMO-DEL-2024-884", pin="8842")
        officer = authenticate_officer(req)
        self.assertIsNotNone(officer)
        self.assertEqual(officer["name"], "Rajesh Sharma")
        token = create_token(officer["officer_id"])
        verified_id = verify_token(token)
        self.assertEqual(verified_id, "LMO-DEL-2024-884")

    def test_invalid_pin_fails(self):
        req = LoginRequest(officer_id="LMO-DEL-2024-884", pin="wrong_pin")
        officer = authenticate_officer(req)
        self.assertIsNone(officer)

    def test_auth_api_endpoint(self):
        client = TestClient(app)
        resp = client.post(
            "/auth/login",
            json={"officer_id": "LMO-DEL-2024-884", "pin": "8842"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["officer"]["name"], "Rajesh Sharma")


class QualityGateTests(unittest.TestCase):
    def test_sharp_image_passes(self):
        # Create a synthetic image with high-frequency pattern (sharp edges)
        arr = np.zeros((300, 300, 3), dtype=np.uint8)
        arr[::10, :] = 255
        arr[:, ::10] = 255
        quality = check_image_quality(arr)
        self.assertGreater(quality["blur_score"], 60.0)

    def test_blurry_flat_image_flagged(self):
        # Flat constant image has zero Laplacian variance (completely blurry/flat)
        arr = np.full((300, 300, 3), 128, dtype=np.uint8)
        quality = check_image_quality(arr)
        self.assertIn("image_too_blurry", quality["issues"])


class DateSeparationTests(unittest.TestCase):
    def test_mfg_and_expiry_exclusion(self):
        # Test the critical bug from pipeline A where adjacent lines borrow dates
        lines = [
            {"text": "MFG DATE: 15/08/2026", "confidence": 0.95, "bbox": [10, 10, 100, 30]},
            {"text": "BEST BEFORE / EXPIRY: 15/02/2027", "confidence": 0.92, "bbox": [10, 35, 100, 55]},
        ]
        mfg, exp = extract_dates_with_separation(lines)
        self.assertIsNotNone(mfg)
        self.assertIsNotNone(exp)
        self.assertEqual(mfg["value"], "15/08/2026")
        self.assertEqual(exp["value"], "15/02/2027")
        self.assertNotEqual(mfg["value"], exp["value"])


class ContextProximityTests(unittest.TestCase):
    def test_mrp_within_distance_accepted(self):
        text = "PRE-PACKED FOOD COMMODITY. MRP INCL. OF ALL TAXES Rs. 145.00"
        line_map = [{"start": 0, "end": len(text), "text": text, "confidence": 0.95}]
        mrp = _find_closest_context_match(MRP_KEYWORDS, MRP_VALUE_PATTERN, text, line_map)
        self.assertIsNotNone(mrp)
        self.assertEqual(mrp["value"], "145.00")

    def test_distant_number_rejected_as_mrp(self):
        # Calories 250 without MRP keyword within 40 chars
        text = "NUTRITIONAL VALUE: Energy 250 kcal, Protein 4.5g, Carbohydrates 35g, Added Sugars 0.0g"
        line_map = [{"start": 0, "end": len(text), "text": text, "confidence": 0.95}]
        mrp = _find_closest_context_match(MRP_KEYWORDS, MRP_VALUE_PATTERN, text, line_map)
        self.assertIsNone(mrp)


class EvidenceUploadApiTests(unittest.TestCase):
    def setUp(self):
        create_tables()
        self.client = TestClient(app)

    def test_quick_scan_with_image(self):
        # Create a small valid test image in memory
        img = Image.new("RGB", (300, 300), color=(200, 200, 200))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        resp = self.client.post(
            "/inspection/quick-scan",
            files={"file": ("test_label.jpg", buf, "image/jpeg")},
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("inspection_id", data)
        self.assertIn("overall_status", data)
        self.assertIn("quality_metrics", data)
        self.assertIn("checks", data)
        self.assertIn("evidence_url", data)


if __name__ == "__main__":
    unittest.main()
