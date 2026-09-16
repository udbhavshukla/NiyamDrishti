# NiyamDrishti AI — Backend Integration Handoff

**From:** Member 3 (Backend + DB + Rule Engine + AI Integration)
**To:** Member 6 (Integration + QA + Security + Deployment)
**Date:** 2026-09-11

---

## 1. Backend Location

- **Local path:** `/Users/udbhav/Documents/VS Code/niyamdrishti-backend/final testing /backend`
- **Repository/branch:** Not yet pushed to a remote repository.

---

## 2. Backend Responsibility

Member 3's backend receives product inspection requests and structured OCR facts, persists them in PostgreSQL (SQLite default for zero-config dev), resolves the active database-backed rule version, and runs a deterministic rule engine (no LLM legal decisions). Inspectors can then review or override the result. Dashboard/list/report endpoints are PostgreSQL-backed. All mutating routes require JWT auth; evidence files are served only to authenticated clients.

---

## 3. Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app — all endpoints
│   ├── auth.py               # JWT: lazy AUTH_SECRET_KEY, get_current_officer, require_auth
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── sample_data.py        # legacy sample store, no longer used by the APIs
│   ├── seed_rules.py         # idempotent Member 2 rule import (python3 -m app.seed_rules)
│   └── services/
│       ├── rule_version_resolver.py
│       └── rule_engine.py    # deterministic engine + is_ecommerce scoping
├── tests/
│   ├── test_rule_engine.py
│   ├── test_review.py
│   ├── test_database_apis.py
│   ├── test_integration_ai.py
│   └── test_bugfix_regressions.py   # NEW — BUG-002/003/007/009 + CORS + multi-panel
├── requirements.txt
├── niyamdrishti.db        # unused SQLite, preserved
├── .env.example
├── PROJECT_STATE.md
├── INTEGRATION_HANDOFF.md
└── BUG_FIX_REPORT.md
```

---

## 4. Database

| Property | Value |
|----------|-------|
| Engine (production) | PostgreSQL 18 (via Postgres.app) |
| Database name | `niyamdrishti` |
| Host / Port | `localhost` / `5432` |
| User | `udbhav` |
| Password | Local trust auth (no password for local connections) |
| Dev fallback | SQLite (`sqlite:///./niyamdrishti.db`) when `DATABASE_URL` unset |
| ORM | SQLAlchemy 2.0.35 |
| Driver | psycopg2-binary 2.9.13 |
| Connection config | `DATABASE_URL` environment variable |

### Tables (5)

| Table | Purpose | Key columns |
|-------|---------|-------------|
| `inspections` | Core inspection record | `inspection_id` (unique), `product_name`, `inspector_id`, `overall_status`, `rule_version`, `confidence`, `is_ecommerce` (NEW) |
| `declarations` | OCR-extracted label fields | `inspection_id` (FK), `field_name`, `value`, `confidence`, `bbox`, `source` |
| `violations` | Compliance failures from rule engine (`FAIL` only) | `inspection_id` (FK), `rule_id`, `field_name`, `severity`, `reason`, `extracted_text` |
| `reviews` | Inspector decisions (human-in-the-loop) | `inspection_id` (FK), `decision`, `comment`, `reviewer_id` |
| `rules` | Versioned regulatory requirements | `rule_id`, `version`, `field_name`, `requirement_type`, `requirement`, `severity`, `active`, `source_reference` |

Tables auto-create on startup via `create_tables()` — no manual migration step needed.
Foreign keys reference `inspections.inspection_id` (string, not integer PK).
15 seeded rules (`is_ecommerce` rules present: `ECOMMERCE_*` field names).

---

## 5. API Contract

### Base URL
```
http://localhost:8000
```
### Swagger UI
```
http://localhost:8000/docs
```

### Authentication (NEW — all mutating routes)

`POST /auth/login` with `{"officer_id": "...", "pin": "..."}` → `{"access_token": "..."}`.
Send `Authorization: Bearer <token>` on protected routes. Missing/bad token → **HTTP 401**.
Test officer: `LMO-DEL-2024-884` / pin `8842`.

Protected: `POST /inspection`, `POST /inspection/{id}/analyze`, `POST /inspection/{id}/review`,
`POST /inspection/quick-scan`, `POST /inspection/{id}/evidence`, `GET /uploads/evidence/{id}/{filename}`.

`AUTH_SECRET_KEY` is mandatory (fail-closed, no fallback). See `.env.example`.

---

### IMPLEMENTED ✅ (all endpoints)

#### `GET /health`
- **Response:** `{"status": "ok", "version": "..."}`

---

#### `POST /auth/login`
- **Request:** `{"officer_id": "...", "pin": "..."}`
- **Response (200):** `{"access_token": "<jwt>", "token_type": "bearer", ...}`
- **500** if `AUTH_SECRET_KEY` unset (fail-closed).

---

#### `POST /inspection`  (auth required)
- **Request:** `{"product_name": "Tata Salt", "inspector_id": "FSO-MH-001", "is_ecommerce": false}`
  - `inspector_id` is taken from the token's officer identity (body value ignored). `is_ecommerce` defaults `false`.
- **Response (201):** inspection with `overall_status: "PENDING"`, generated `inspection_id` (`INS-YYYYMMDD-XXXX`)

---

#### `GET /inspection/{inspection_id}`
- Full inspection including declarations, violations, reviews, `is_ecommerce`
- **404** if missing

---

#### `POST /inspection/quick-scan`  (auth required)
- Single multipart image upload; requires `file=`.
- Optional `is_ecommerce` query parameter (`true`/`false`/`None`).
- Runs OCR → rules → violation analysis in one call. Implicitly public (physical) context → e-commerce rules `NOT_APPLICABLE`.
- Non-image `Content-Type` / corrupt / empty file → **HTTP 400** (`{"detail": {"error": "invalid_image_file", ...}}`); no inspection record is orphaned.
- **Response (200):** `{"inspection_id", "product_name", "overall_status", "rule_version", "confidence", "is_ecommerce", "declarations", "checks", "violations", "evidence_url", ...}`

---

#### `POST /inspection/{inspection_id}/evidence`  (auth required)
- Multipart `file=`, optional `panel_type` (`front`/`back`/other), optional `is_ecommerce` query.
- Validates image **before any disk write** (BUG-003 → 400 on invalid/corrupt/empty/non-image).
- Safe server-generated filename: `{panel_type}_{timestamp}_{uuid}.{ext}` (BUG-009; client filename discarded).
- **Multi-panel merge:** repeated uploads merge OCR facts by `field_name`; higher-confidence value wins; prior `PASS/FAIL/DECLARED` preserved; `declarations`/`violations` recomputed; `reviews` left untouched.
- **Response (200):** includes `evidence_url` like `/uploads/evidence/{inspection_id}/{filename}`.

---

#### `GET /uploads/evidence/{inspection_id}/{filename}`  (auth required)
- Auth via `Authorization: Bearer <token>` **or** `?token=<token>` (for `<img>` tags).
- Filename regex-whitelist (`[A-Za-z0-9!()@._-]+`) + `os.path.commonpath` containment → traversal rejected (**HTTP 400**) (BUG-009).
- Returns the image file via `FileResponse`.
- **401** unauth, **404** missing.

---

#### `POST /inspection/{inspection_id}/analyze`  (auth required)
- **Purpose:** Persist structured OCR facts, resolve current rule version, run deterministic engine
- **Request body** (field → OCR fact):
```json
{
  "product_name": {"value": "ABC Detergent", "confidence": 0.97, "bbox": [20, 30, 200, 70]},
  "mrp": {"value": "₹120", "confidence": 0.55, "bbox": [300, 400, 450, 450]},
  "is_ecommerce": false
}
```
- Optional per field: `source` (default `ocr`), `evidence_image`. Optional top-level `is_ecommerce`.
- **Response 200:**
```json
{
  "inspection_id": "INS-20260911-xxxx",
  "overall_status": "REVIEW_REQUIRED",
  "rule_version": "1",
  "confidence": 0.76,
  "is_ecommerce": false,
  "checks": [
    {"rule_id": "LM-PC-006-1A", "field": "...", "status": "PASS|FAIL|REVIEW_REQUIRED|NOT_APPLICABLE", ...}
  ],
  "violations": [],
  "warnings": []
}
```
- **`is_ecommerce` scoping (BUG-002):** rules with `ECOMMERCE_*` fields are skipped with status `NOT_APPLICABLE` on physical scans, evaluated on e-commerce scans, and `REVIEW_REQUIRED` when the context is unknown.
- `overall_status` is only `PASS`, `FAIL`, or `REVIEW_REQUIRED`
- Re-analysis replaces declarations and machine violations; reviews are kept
- Low OCR confidence (`< 0.90`) never becomes `FAIL`; unverified/missing legal source never becomes PASS/FAIL

---

#### `POST /inspection/{inspection_id}/review`  (auth required)
- **Request:**
```json
{"decision": "PASS", "comment": "Label complete", "reviewer_id": "FSO-MH-001"}
```
- `reviewer_id` from body is overridden by the token's officer identity (as reviewer). `decision` must be `PASS|FAIL|REVIEW_REQUIRED`.
- Writes a `reviews` row and sets `inspections.overall_status`. **404** if inspection missing.

---

#### `GET /rules`, `GET /rules/current`
- Lists stored rule rows (15); current resolver returns active/effective version rules.

#### `GET /inspections`, `GET /dashboard`, `GET /inspection/{id}/report`
- PostgreSQL-backed list/stats/report endpoints (page/page_size/status filters; report 404 on missing).

---

### NOT YET IMPLEMENTED ❌

- Rate limits / request size limits, HTTPS, deployment (Member 6 scope).
- Field-level evaluation of Member 2's requirement types by the generic rule evaluator
  (currently routes to `REVIEW_REQUIRED`).

---

## 6. Frontend Integration

### Communication
- HTTP REST JSON.
- CORS: explicit origins by default (`CORS_ORIGINS` env, comma-separated). Credentials (cookies /
  Authorization headers) only when origins are explicit; `CORS_ORIGINS=*` disables credentials.
- Evidence `<img>` tags can't send headers → backend accepts `?token=` query param; the frontend
  (`frontend/src/api.js`) appends `?token=<jwt>` from `localStorage('niyam_token')` to evidence URLs.

### Typical Endpoint Sequence
```
0. POST /auth/login                         → access_token (store as niyam_token)
1. POST /inspection                         → create inspection, get inspection_id
2. POST /inspection/{id}/analyze            → send OCR JSON, get PASS/FAIL/REVIEW_REQUIRED
3. GET  /inspection/{id}                    → persisted state
4. GET  /uploads/evidence/{id}/{filename}?token=...   → evidence image
5. POST /inspection/{id}/review             → inspector decision (PASS/FAIL/REVIEW_REQUIRED)
6. GET  /inspections                        → paginated list
7. GET  /dashboard                          → real stats
8. GET  /inspection/{id}/report             → full report
```

---

## 7. Environment Variables

See `.env.example`. Used:

| Variable | Required | Notes |
|----------|----------|-------|
| `AUTH_SECRET_KEY` | **YES** | Fail-closed; login → 500 and protected routes → 401 if unset |
| `DATABASE_URL` | No | Defaults to local `niyamdrishti.db` SQLite; set to PostgreSQL for prod |
| `CORS_ORIGINS` | No | Comma-separated origins; default localhost 5173/3000; `*` disables credentials |
| `EVIDENCE_STORAGE_PATH` | No | Default `./uploads/evidence` |
| `HOST` / `PORT` | No | Defaults `0.0.0.0:8000` |

---

## 8. Setup (Member 6)

```bash
cd "/Users/udbhav/Documents/VS Code/niyamdrishti-backend/final testing /backend"
pip install -r requirements.txt

# Mandatory: set a strong JWT secret
export AUTH_SECRET_KEY="$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")"

# Optional: use PostgreSQL (defaults to SQLite otherwise)
export DATABASE_URL="postgresql://udbhav@localhost:5432/niyamdrishti"

# Optional: re-seed rules (idempotent — safe to run any time)
python3 -m app.seed_rules

python3 -m uvicorn app.main:app --reload --port 8000
```
Tables auto-create on startup. `/docs` gives interactive Swagger UI (all protected routes need the Bearer token).

---

## 9. Database Verification

```bash
/Applications/Postgres.app/Contents/Versions/18/bin/psql -U udbhav -d niyamdrishti -c "\dt"
/Applications/Postgres.app/Contents/Versions/18/bin/psql -U udbhav -d niyamdrishti \
  -c "SELECT rule_id, version, active FROM rules ORDER BY rule_id;"     # expect 15 rows
/Applications/Postgres.app/Contents/Versions/18/bin/psql -U udbhav -d niyamdrishti \
  -c "SELECT inspection_id, product_name, overall_status, is_ecommerce FROM inspections;"
```

---

## 10. Tests

```bash
cd "/Users/udbhav/Documents/VS Code/niyamdrishti-backend/final testing /backend"
python3 -m unittest discover -s tests -v
```

Result: **49 tests, all pass — on both SQLite (default) and PostgreSQL** (verified 2026-09-11).
Regression suite covers: BUG-002 e-commerce scoping (both contexts), BUG-003 invalid/empty/non-image uploads,
BUG-007 missing-secret fail-closed, BUG-009 evidence auth + path traversal, CORS preflight, multi-panel merge.
Multi-panel merge flush uses `db.expunge(stale)` so no SQLAlchemy identity-map warnings appear.
See `FINAL_TEST_REPORT.md` for the live end-to-end verification record.

---

## 11. Known Issues / Notes

1. **No rate limits / request size limits.**
2. **No HTTPS** locally.
3. **`psql` not on PATH** — use Postgres.app binary path.
4. **Rule-engine coverage:** Member 2's `mandatory_declaration` / `prohibition` / `format_requirement` /
   `conditional_exemption` / `scope_limit` requirements are not evaluated generically; they return
   `REVIEW_REQUIRED` (deterministic, human-in-the-loop). Extending `_evaluate_requirement` is a Member 6 decision.
5. **Rule count label:** task prose says "14 rules", the supplied JSON contains 15 records; seed imports verbatim (15).
6. **Resolver version behavior:** `get_current_rules` returns only rules of the newest effective version present.
7. **Identity map note:** multi-panel re-analysis uses `synchronize_session=False` deletes + `db.expire_all()`
   to avoid stale-row warnings when recycled PKs are flushed.

---

## 12. Integration Notes

- JWT auth on all mutating routes; `AUTH_SECRET_KEY` mandatory (fail-closed).
- Evidence served only to authenticated clients; server-generated filenames; traversal blocked.
- CORS explicit-origin by default (env-configurable); credentials only with explicit origins.
- Tables via `Base.metadata.create_all()`, no Alembic.
- Inspection IDs are strings: `INS-YYYYMMDD-XXXX`.
- Datetimes are UTC-naive in DB.
- `niyamdrishti.db` SQLite is unused and preserved.
- Rule engine does **not** call an LLM.
- A stored rule is treated as legally usable only when `source_reference` is non-empty and
  does not contain `LEGAL SOURCE VERIFICATION REQUIRED`.
- `sample_data.py` still exists for reference but is no longer imported by the API.

---

## 13. Current Status

### DONE ✅
- FastAPI + CORS (explicit, env-driven) + PostgreSQL/SQLite (5 tables)
- JWT auth (`/auth/login`, `require_auth`, fail-closed secret)
- `POST /inspection` (auth), `GET /inspection/{id}`, `POST /inspection/{id}/analyze` (auth, `is_ecommerce`)
- `POST /inspection/quick-scan` (auth; 400 on invalid image, no orphaned records)
- `POST /inspection/{id}/evidence` (auth; validated before disk write; multi-panel merge)
- `GET /uploads/evidence/{id}/{filename}` (auth via header or `?token=`)
- `POST /inspection/{id}/review` (auth; reviewer identity from token)
- Rule version resolver + deterministic engine + `is_ecommerce` scoping (BUG-002)
- **15 Member 2 rules seeded** (idempotent `python3 -m app.seed_rules`)
- `GET /rules`, `GET /rules/current`, `GET /inspections`, `GET /dashboard`, `GET /inspection/{id}/report`
- **49 automated tests pass (SQLite + PostgreSQL)**; live end-to-end curl + psql verification recorded
  in `FINAL_TEST_REPORT.md` (2026-09-11)