# Project Status

Last verified: backend FINAL TEST — **49 passed / 0 failed / 0 errors / 0 skipped**
on SQLite and PostgreSQL 18.6 (evidence: `docs/FINAL_TEST_REPORT.md`).

## COMPLETED
- FastAPI backend: 14 routes (health, auth, inspection CRUD, rules, analyze,
  evidence, quick-scan, review, list, dashboard, report, secure evidence serving).
- Deterministic rule engine + DB-driven version resolver (15 seeded rules, idempotent).
- E-commerce scoping fix (BUG-002): physical scans no longer false-fail.
- Upload validation (BUG-003): 400 `invalid_image_file` / `empty_file`, zero orphans.
- Fail-closed `AUTH_SECRET_KEY` (BUG-007) + authenticated, traversal-proof evidence
  serving with server-generated filenames (BUG-009).
- Officer auth with token-identity precedence; multi-panel merge (higher confidence
  wins); append-only human reviews; dashboard + full report from the DB.
- 49-test backend suite; one-command `setup.sh`/`setup.bat`; `start_demo` scripts;
  React client with offline fallback; Flutter client with real API service layer.
- Docs: `docs/` (10 guides + 4 imported verification reports), `team/` (6 files).

## KNOWN ISSUES (with owners)
| ID | Issue | Owner |
|---|---|---|
| BUG-004 | InspectorHome shows hardcoded officer profile | Member 5 |
| BUG-005 | GuidedScan timer race | Member 5 |
| BUG-006 | Hardcoded demo PINs in frontend offline fallback | Member 5 (+ Member 6 for credential store) |
| BUG-008 | Flutter client is single-panel; backend supports multi-panel | Member 4 |
| SEC-1 | Read endpoints (`GET /inspection/{id}`, `/inspections`, `/dashboard`, `/report`, `/rules*`) are unauthenticated in this MVP | Member 6 (policy) |
| SEC-2 | Demo officer PINs hardcoded (documented, demo-only) | Member 6 |
| BUILD-1/2 | `npm run build` / `flutter analyze` not re-verified (SDKs absent in test env) | Members 5/6, 4/6 |

## NOT COMPLETED
- Production deployment (hosting, TLS/HTTPS, reverse proxy, process supervision).
- Real officer credential store replacing demo PINs.
- Rate limiting, audit logging, standard JWT library with rotation.
- Multi-panel upload flow in the Flutter app.
- CI pipeline (backend tests + `npm run build` + `flutter analyze`).

## REMAINING DEVELOPMENT (by member)
- **Member 1:** OCR accuracy (engines/weights/languages); keep the `OCRField` contract.
- **Member 2:** Rule stewardship for new amendments; keep `requirement_type` vocabulary
  and `ECOMMERCE_` prefix convention.
- **Member 3:** Authenticate read endpoints if policy requires; nothing blocking.
- **Member 4:** Multi-panel flow; verify `flutter analyze` + release build.
- **Member 5:** Fix BUG-004/005/006 against the live backend; verify `npm run build`.
- **Member 6:** Env/hosting, credential store, rate limits, HTTPS, CI, QA sign-off.

## DEPLOYMENT REQUIREMENTS
PostgreSQL instance, strong `AUTH_SECRET_KEY`, explicit `CORS_ORIGINS`, TLS
termination, static hosting for the React build, API base URL configured in both
clients, seeded rules verified (`seed_rules()` inserts 15, re-run inserts 0).
Full checklist: `docs/DEPLOYMENT.md`.
