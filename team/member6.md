# Member 6 — Integration, QA, Security & Deployment

## Responsibility
Bring the pieces together: reproducible setup, QA, security hardening, deployment.
Own everything needed to run the system on a fresh machine and in production.

## Exact files / folders related to this work
| Path | Role |
|---|---|
| `setup.sh` / `setup.bat` | One-command setup: venv -> `pip install -r requirements.txt` -> `create_tables(); seed_rules()` -> `npm install` (verified commands, Node optional) |
| `start_demo.sh` / `start_demo.bat` | Launches backend `:8000` + frontend `:5173` together |
| `backend/requirements.txt` | Backend dependency pins to install and audit |
| `.env.example` (repo root copy) | Placeholder-only env template (never real secrets) |
| `.gitignore` (repo root copy) | Keeps secrets, DBs, uploads, and generated files out of git |
| `RUN_PROJECT.md`, `PROJECT_STATUS.md` | Run instructions and status board to maintain |
| `docs/` | Verification evidence (`FINAL_TEST_REPORT.md`, `BUG_FIX_REPORT.md`, …) |

## Important APIs / components
- Health gate: `GET /health`; API docs: `GET /docs` (Swagger, auto-generated).
- Env contract: `DATABASE_URL`, `AUTH_SECRET_KEY` (required), `HOST`/`PORT`,
  `CORS_ORIGINS`, `EVIDENCE_STORAGE_PATH`.

## Dependencies on other members
- **Member 3:** backend startup command, test suite (`python -m unittest discover -s tests`).
- **Member 5:** frontend dev/build commands (`npm run dev`, `npm run build`).
- **Member 4:** Flutter build requirements (SDK `>=3.0.0 <4.0.0`).

## What to understand before modifying / deploying
1. Backend test gate is 49/49 on SQLite AND PostgreSQL 18.6 (see `docs/FINAL_TEST_REPORT.md`).
2. Security posture (see `docs/SECURITY.md`): fail-closed secret, authenticated evidence,
   no wildcard CORS with credentials. Still missing: rate limiting, HTTPS, production
   JWT library — all tracked in `PROJECT_STATUS.md`.
3. Never commit `.env`, `*.db`, `uploads/evidence/*`, or the root `.env.example`'s
   predecessor value — the original project's root example file contained a real-looking
   secret and was deliberately replaced with placeholders here.
