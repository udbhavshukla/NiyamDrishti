# Member 3 — FastAPI Backend, Database, Rule Engine, Integration Contracts

## Responsibility
Own the server: FastAPI app, PostgreSQL/SQLite layer, inspection/analyze/evidence/
review/dashboard/report APIs, AI/OCR integration interface, structured declaration
processing, rule version resolver, deterministic rule engine, evidence storage,
backend testing (49/49), and the contracts the apps build against.

## Exact files / folders related to this work
| Path | Role |
|---|---|
| `backend/app/main.py` | All 14 API routes + business logic (inspection CRUD, analyze, evidence upload/merge, quick-scan, review, list, dashboard, report, secure evidence serving) |
| `backend/app/auth.py` | Officer registry, HMAC-SHA256 tokens, `require_auth` dependency |
| `backend/app/database.py` | Engine/session; SQLite default, PostgreSQL via `DATABASE_URL`; auto-creates tables |
| `backend/app/models.py` | 5 tables: `inspections`, `declarations`, `violations`, `reviews`, `rules` |
| `backend/app/schemas.py` | Pydantic request/response contracts shared with React + Flutter |
| `backend/app/seed_rules.py` | Idempotent seeder for the 15 legal rules |
| `backend/app/services/ai_ocr.py` | OCR integration interface (`analyze_package_label`) |
| `backend/app/services/rule_engine.py` | Deterministic compliance evaluation |
| `backend/app/services/rule_version_resolver.py` | Active-version selection from DB rows |
| `backend/tests/` | 5 files, 49 tests (see `docs/TESTING.md` in `docs/`) |
| `backend/requirements.txt` | Pinned backend dependencies |

## Important APIs / components
- Auth: `POST /auth/login`, `GET /auth/me` (all inspection mutations need Bearer token).
- Flow: `POST /inspection` -> `POST /inspection/{id}/evidence` (per panel) or
  `POST /inspection/quick-scan` (one-shot) -> `POST /inspection/{id}/analyze` (raw OCR facts)
  -> `POST /inspection/{id}/review` -> `GET /inspection/{id}/report`, `GET /dashboard`.
- Evidence: `GET /uploads/evidence/{inspection_id}/{filename}` accepts Bearer header
  or `?token=` query; traversal-proof; server-generated filenames.
- Engine statuses: `PASS` / `FAIL` / `REVIEW_REQUIRED` / `NOT_APPLICABLE`; overall =
  FAIL if any FAIL, else REVIEW_REQUIRED if any REVIEW_REQUIRED, else PASS.

## Dependencies on other members
- **Member 1:** supplies OCR quality; backend defines the `OCRField` contract.
- **Member 2:** supplies rule content; backend stores, versions, and executes it.
- **Members 4/5:** consume the APIs above; breaking contract changes need coordination.
- **Member 6:** deploys this service; needs `.env.example` values + `RUN_PROJECT.md`.

## What to understand before modifying code
1. Identity always comes from the token (`officer.officer_id` wins over any body field).
2. `AUTH_SECRET_KEY` has no fallback — missing secret fails closed (login 500, guarded 401).
3. Image validation order on upload: MIME type -> empty -> decodable bytes; 400s with
   `invalid_image_file` / `empty_file` codes; quick-scan deletes orphan rows on failure.
4. Re-analysis replaces machine rows only; `reviews` rows are never deleted.
5. Multi-panel merge keeps the higher-confidence reading per field; `db.expunge(stale)`
   after bulk deletes avoids identity-map collisions (see `docs/BUG_FIX_REPORT.md`).
