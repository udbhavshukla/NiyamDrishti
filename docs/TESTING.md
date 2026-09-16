# Testing

## Backend gate (verified)
```
cd backend
python -m unittest discover -s tests -v
```
Result on record: **49 passed, 0 failed, 0 errors, 0 skipped** — on SQLite
(default) and on PostgreSQL 18.6 via `DATABASE_URL`
(full evidence: `FINAL_TEST_REPORT.md`).

## What the 5 files cover (49 = 25 + 7 + 9 + 3 + 5)
| File | Tests | Scope |
|---|---|---|
| `tests/test_bugfix_regressions.py` | 25 | Regression coverage for every fixed bug: e-commerce scoping, auth guards, invalid-image uploads, CORS config, fail-closed secret, evidence security, multi-panel merge |
| `tests/test_database_apis.py` | 7 | Inspection CRUD, list, dashboard, report endpoints |
| `tests/test_integration_ai.py` | 9 | OCR pipeline + analyze integration |
| `tests/test_review.py` | 3 | Review recording and status update |
| `tests/test_rule_engine.py` | 5 | Engine evaluation and versioning |

Tests set `AUTH_SECRET_KEY=test-key-for-sih-26034` via `os.environ.setdefault`
(test-only; never a production secret).

## Manual verification performed (see `FINAL_TEST_REPORT.md`)
Live uvicorn + PostgreSQL checks: 401s without token on all mutating endpoints,
token-identity precedence over spoofed body fields, deterministic repeat runs,
400 codes for corrupt/empty/non-image uploads with zero orphan rows, evidence
401/200/404 matrix, traversal blocked, multi-panel merge counts, CORS preflight,
missing-secret fail-closed behavior, seed idempotency (15 rules, 0 new on re-run).

## Not covered here (honest)
- `npm run build` for the React app and `flutter analyze/build` for the mobile app
  were not re-verified in the backend test environment (Node/Flutter SDKs absent).
  Member 5/6 and Member 4/6 own those gates — see `PROJECT_STATUS.md`.
