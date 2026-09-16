# NIYAMDRISHTI AI — PROJECT STATE

**Last updated:** 2026-09-11 — Member 3 FINAL VERIFICATION (49/49 tests on SQLite AND PostgreSQL, live end-to-end checks, FINAL_TEST_REPORT.md)
**Member:** 3 (Backend + DB + Rule Engine + AI Integration)
**Deadline:** 2026-09-11 14:00 IST

---

## Current Phase: Core Compliance Pipeline + Security Hardening COMPLETE ✅

### What Works

| Component | Status |
|-----------|--------|
| FastAPI app starts | ✅ |
| CORS enabled (explicit, env-driven origins) | ✅ |
| **AUTH_SECRET_KEY required (fail-closed)** | ✅ |
| JWT auth — /auth/login, require_auth dependency | ✅ |
| POST /inspection — authenticated (inspector from token) | ✅ |
| POST /inspection/{id}/analyze — authenticated, is_ecommerce support | ✅ |
| POST /inspection/{id}/review — authenticated (reviewer from token) | ✅ |
| POST /inspection/quick-scan — authenticated, invalid-image 400, orphan cleanup | ✅ |
| POST /inspection/{id}/evidence — authenticated, server-generated safe filenames, multi-panel merge | ✅ |
| GET /uploads/evidence/{id}/{filename} — Bearer header OR ?token= query param | ✅ |
| E-commerce rule scoping (BUG-002) — NOT_APPLICABLE/REVIEW_REQUIRED/FAIL per context | ✅ |
| Image validation before disk write (BUG-003) — 400 on corrupt/empty/non-image | ✅ |
| Evidence security (BUG-009) — traversal blocked, auth required, safe filenames | ✅ |
| Deterministic rule engine (no LLM) | ✅ |
| Rule version resolver (database-driven) | ✅ |
| GET /health | ✅ |
| GET /inspection/{id} | ✅ |
| GET /rules and GET /rules/current | ✅ |
| GET /inspections (paginated, status filter) | ✅ |
| GET /dashboard | ✅ |
| GET /inspection/{id}/report | ✅ |
| PostgreSQL 18 database (niyamdrishti) | ✅ |
| SQLite fallback for zero-config dev | ✅ |

### Bug Fixes Verified (2026-09-11)

| Bug ID | Description | Status |
|--------|-------------|--------|
| BUG-001 | `setup.sh` import path `seed_rules` → `app.seed_rules` | ✅ CONFIRMED FIXED (already in place) |
| BUG-002 | E-commerce field rules (LM-PC-006-10A, LM-PC-006-10B) fire FAIL on physical scans | ✅ FIXED — `ECOMMERCE_` prefix scoping in rule_engine |
| BUG-003 | Invalid/corrupt images written to disk before analysis | ✅ FIXED — validated in-memory before file I/O |
| BUG-007 | AUTH_SECRET_KEY has hardcoded fallback in source code | ✅ FIXED — `_get_secret_key()` reads env only, raises 500/returns None when missing |
| BUG-009 | Evidence file served as public static assets without auth | ✅ FIXED — authenticated GET route with Bearer/?token= support |

### What Does NOT Work Yet

| Component | Status |
|-----------|--------|
| Non-deterministic (LLM-based) legal evaluation | ❌ by design — never used |
| Engine support for `prohibition`, `format_requirement`, `conditional_exemption`, `scope_limit` types | ⚠️ routes to `REVIEW_REQUIRED` (human-in-the-loop) |

---

## Authentication

**AUTH_SECRET_KEY** is **mandatory**. The app fails closed:
- `/auth/login` returns HTTP 500 if secret is not set.
- All `require_auth` endpoints return HTTP 401 if the token is missing/invalid/expired.
- No fallback, no hardcoded secret in source code.

**Test credentials:** `LMO-DEL-2024-884` / pin `8842` (inspector_id and officer_id in DB).

**Protected endpoints:** POST /inspection, POST /inspection/{id}/analyze, POST /inspection/{id}/review, POST /inspection/quick-scan, POST /inspection/{id}/evidence, GET /uploads/evidence/*.

## E-Commerce Scoping (BUG-002)

Rules whose `field_name` starts with `ECOMMERCE_` are e-commerce-only:

| Context | Behavior |
|---------|----------|
| `is_ecommerce=False` (physical scan default) | Status = `NOT_APPLICABLE`; skipped; never triggers FAIL |
| `is_ecommerce=None` (unknown context) | Status = `REVIEW_REQUIRED`; cannot confirm without context |
| `is_ecommerce=True` (e-commerce upload) | Rule evaluated normally (PASS / FAIL / REVIEW_REQUIRED) |

`POST /inspection` sets `is_ecommerce` from the request body (defaults to `False`).
`POST /inspection/quick-scan` and `POST /inspection/{id}/analyze` accept `?is_ecommerce=true|false|None` query parameter.

## Evidence Security (BUG-009)

- No public static mount on `/uploads` — removed entirely.
- Evidence served via **authenticated** `GET /uploads/evidence/{inspection_id}/{filename}`.
- Auth accepted as `Authorization: Bearer <token>` header **or** `?token=<token>` query param (for `<img>` tags).
- Filenames generated server-side: `{panel_type}_{timestamp}_{uuid}.{ext}`. User-supplied filenames are discarded.
- Traversal blocked: regex whitelist on filenames + `os.path.commonpath` containment check → HTTP 400.

## Multi-Panel Evidence Merge

Multiple evidence uploads to the same inspection now merge `ocr_facts` by `field_name`:
- Higher `OCR confidence` wins per field.
- Prior `PASS/FAIL/DECLARED` status is preserved when the new value is equal.
- `declarations` and `violations` are recomputed from the full merged fact set.
- `review` rows are untouched by re-analysis.

## Files Changed (2026-09-11)

```
backend/
├── .env.example                 # UPDATED — AUTH_SECRET_KEY placeholder, CORS_ORIGINS explicit
├── PROJECT_STATE.md             # THIS FILE
├── INTEGRATION_HANDOFF.md       # UPDATED
├── BUG_FIX_REPORT.md            # NEW — per-bug root cause + fix + test summary
├── app/
│   ├── auth.py                  # UPDATED — lazy secret, get_officer_by_token, require_auth
│   ├── main.py                  # UPDATED — auth wiring, CORS, evidence route, 400 handling, multi-panel
│   ├── schemas.py               # UPDATED — is_ecommerce, NOT_APPLICABLE in AnalysisCheck pattern
│   ├── models.py                # unchanged
│   ├── database.py              # unchanged
│   ├── seed_rules.py            # unchanged
│   └── services/
│       ├── rule_engine.py       # UPDATED — is_ecommerce param, ECOMMERCE_ scoping
│       └── rule_version_resolver.py  # unchanged
├── tests/
│   ├── test_database_apis.py    # UPDATED — auth headers
│   ├── test_integration_ai.py   # UPDATED — auth headers
│   ├── test_rule_engine.py      # unchanged
│   ├── test_review.py           # unchanged
│   └── test_bugfix_regressions.py  # NEW — 25 regression tests (BUG-002/003/007/009, multi-panel, CORS)
frontend/
└── src/
    └── api.js                   # UPDATED — evidence URLs include ?token= for <img> auth
```

## Database

**PostgreSQL 18** (primary, production):
```
postgresql://udbhav@localhost:5432/niyamdrishti
```

**SQLite** (zero-config dev, set via `DATABASE_URL` or default):
```
sqlite:///./niyamdrishti.db
```

5 tables: `inspections`, `declarations`, `violations`, `reviews`, `rules`
New columns since last update: `inspections.is_ecommerce` (boolean, default False).

## API Endpoints

| Method | Path | Auth | Status |
|--------|------|------|--------|
| GET | /health | — | ✅ |
| POST | /auth/login | — | ✅ (returns `access_token`) |
| POST | /inspection | ✅ require_auth | ✅ |
| GET | /inspection/{id} | — | ✅ |
| POST | /inspection/{id}/analyze | ✅ require_auth | ✅ (`?is_ecommerce=` query) |
| POST | /inspection/{id}/review | ✅ require_auth | ✅ |
| POST | /inspection/quick-scan | ✅ require_auth | ✅ (`?is_ecommerce=` query) |
| POST | /inspection/{id}/evidence | ✅ require_auth | ✅ (`?is_ecommerce=` query) |
| GET | /uploads/evidence/{id}/{fn} | ✅ Bearer or ?token= | ✅ |
| GET | /rules | — | ✅ |
| GET | /rules/current | — | ✅ |
| GET | /inspections | — | ✅ |
| GET | /dashboard | — | ✅ |
| GET | /inspection/{id}/report | — | ✅ |

## CORS

Configured via `CORS_ORIGINS` env var (comma-separated). Default explicit origins: `localhost:5173`, `localhost:3000`, `127.0.0.1:5173`, `127.0.0.1:3000`.

**Credentials (cookies / Authorization headers) are only allowed when origins are explicit.** Setting `CORS_ORIGINS=*` disables `allow_credentials` — the `?token=` query param on the evidence endpoint provides an alternative for `<img>` tags.

## Commands

```bash
cd "/Users/udbhav/Documents/VS Code/niyamdrishti-backend/final testing /backend"
pip install -r requirements.txt

# Set AUTH_SECRET_KEY (mandatory for login + protected endpoints)
export AUTH_SECRET_KEY="your-strong-secret-here"

# Seed rules (idempotent)
python3 -m app.seed_rules

# Start server
python3 -m uvicorn app.main:app --reload --port 8000

# Run all tests (49 tests, all passing — SQLite AND PostgreSQL modes)
python3 -m unittest discover -s tests -v
# PostgreSQL mode:
#   export DATABASE_URL="postgresql://udbhav@localhost:5432/niyamdrishti"
```

## Final Verification (2026-09-11)

- **49/49 tests pass** on SQLite (default, 0.755 s) and PostgreSQL (0.921 s).
- Live curl + psql verification of auth 401s, BUG-002 scoping (both contexts), image validation 400s,
  evidence security, multi-panel merge, CORS, secret fail-closed, PostgreSQL persistence and seed
  idempotency — all passed. See `FINAL_TEST_REPORT.md`.
- Multi-panel flush clean-up: stale loaded rows are `db.expunge()`d before re-insert (no SAWarning).
- `niyamdrishti.db` SQLite is the zero-config default; PostgreSQL is the primary production DB.
