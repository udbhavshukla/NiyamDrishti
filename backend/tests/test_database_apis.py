"""Minimal tests for the seeded rules and the PostgreSQL-backed APIs.

The 15 rule IDs below are exactly the records supplied by Member 2 in the
MEMBER 2 VERIFIED RULE DATA block (the task message labels the count as
"14", but the supplied JSON contains 15 records; the seed imports exactly
what was supplied and nothing else).
"""

import os

os.environ.setdefault("AUTH_SECRET_KEY", "test-key-for-sih-26034")

import unittest

from fastapi.testclient import TestClient

from app.database import create_tables
from app.main import app

SUPPLIED_RULE_IDS = [
    "LM-PC-006-1A",
    "LM-PC-006-1B",
    "LM-PC-006-1C",
    "LM-PC-006-1D",
    "LM-PC-006-1E",
    "LM-PC-006-2",
    "LM-PC-006-3",
    "LM-PC-007-FONT",
    "LM-PC-009-LANG",
    "LM-PC-018-2",
    "LM-PC-026-EXEMPT",
    "LM-PC-003-SCOPE",
    "LM-PC-006-10-ECOM-V1",
    "LM-PC-006-10A-COO-2026",
    "LM-PC-006-10A-COO-2027",
]

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


def _client() -> TestClient:
    create_tables()
    return TestClient(app)


def _create_inspection(client: TestClient) -> str:
    resp = client.post(
        "/inspection",
        json={"product_name": "Test Product", "inspector_id": "FSO-TST-001"},
        headers=_auth(),
    )
    assert resp.status_code == 201
    return resp.json()["inspection_id"]


class SeededRulesTests(unittest.TestCase):
    def test_all_supplied_rules_are_seeded(self):
        client = _client()
        resp = client.get("/rules")
        self.assertEqual(resp.status_code, 200)
        rule_ids = {rule["rule_id"] for rule in resp.json()}
        self.assertEqual(rule_ids, set(SUPPLIED_RULE_IDS))
        self.assertEqual(len(rule_ids), len(SUPPLIED_RULE_IDS))

    def test_rule_resolver_sees_seeded_rules(self):
        client = _client()
        resp = client.get("/rules/current")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIsNotNone(body["rule_version"])
        self.assertTrue(body["rules"])


class DatabaseApiTests(unittest.TestCase):
    def test_list_inspections_reads_db(self):
        client = _client()
        insp_id = _create_inspection(client)
        resp = client.get("/inspections")
        self.assertEqual(resp.status_code, 200)
        ids = [item["id"] for item in resp.json()["inspections"]]
        self.assertIn(insp_id, ids)

    def test_dashboard_reads_db(self):
        client = _client()
        _create_inspection(client)
        resp = client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.json()["stats"]["total_inspections"], 1)

    def test_report_reads_db(self):
        client = _client()
        insp_id = _create_inspection(client)
        resp = client.get(f"/inspection/{insp_id}/report")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["inspection_id"], insp_id)

    def test_missing_report_returns_404(self):
        client = _client()
        resp = client.get("/inspection/DOES-NOT-EXIST/report")
        self.assertEqual(resp.status_code, 404)

    def test_analyze_then_review_flow(self):
        client = _client()
        insp_id = _create_inspection(client)
        resp = client.post(
            f"/inspection/{insp_id}/analyze",
            json={
                "MRP_RETAIL_SALE_PRICE": {"value": "Rs 120", "confidence": 0.97},
                "NET_QUANTITY": {"value": "500 g", "confidence": 0.95},
            },
            headers=_auth(),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            resp.json()["overall_status"],
            ("PASS", "FAIL", "REVIEW_REQUIRED"),
        )
        resp = client.post(f"/inspection/{insp_id}/review", json={"decision": "PASS"}, headers=_auth())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["overall_status"], "PASS")
        resp = client.get(f"/inspection/{insp_id}")
        self.assertEqual(resp.json()["overall_status"], "PASS")


if __name__ == "__main__":
    unittest.main()