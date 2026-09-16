# NiyamDrishti AI — AI-assisted Legal Metrology Inspection Platform

## What it is
NiyamDrishti AI helps **Legal Metrology Officers** verify pre-packaged commodity
labels against the **Legal Metrology (Packaged Commodities) Rules, 2011**.
An officer photographs a label; OCR extracts the statutory declarations; a
**deterministic, database-driven rule engine** returns an explained verdict
(PASS / FAIL / REVIEW_REQUIRED); the officer reviews and confirms.

## Problem
Manual label checks are slow, inconsistent between officers, and hard to audit —
and e-commerce listings create a second compliance surface (Rules 6(10)/6(10A))
that physical-only inspection mishandles.

## Target users
Field officers (Flutter mobile app), desk officers and reviewers (React portal),
legal team (rule data), enforcement command (dashboard + reports).

## System architecture
```
Flutter app ──┐
              ├──> FastAPI :8000 ──> SQLite (default) / PostgreSQL
React :3000 ──┘                              └── uploads/evidence/<id>/
```
- **Backend** (`backend/`): 14 REST endpoints, 5-table schema, HMAC-token auth,
  versioned rule engine, secure evidence storage, human review, dashboard/report.
- **AI/OCR** (`backend/app/services/ai_ocr.py`): quality gate -> preprocessing ->
  EasyOCR/Tesseract/offline-simulator cascade -> 9 canonical fields
  (value + confidence + bbox). OCR extracts facts; it never decides compliance.
- **Rule engine** (`backend/app/services/rule_engine.py`): evaluates facts against
  one DB-resolved rule version; low confidence or physical-measurement checks route
  to `REVIEW_REQUIRED`, never to a guess.
- **Frontend** (`frontend/`): React 18 + Vite login, dashboard, guided scan,
  compliance results, review override, offline fallback.
- **Mobile** (`mobile/`): Flutter capture-and-upload client with real API service.

## Technology stack
FastAPI · Uvicorn · Pydantic v2 · SQLAlchemy 2 · SQLite/PostgreSQL 18 ·
OpenCV · Pillow · NumPy · EasyOCR/Tesseract · React 18 · Vite 6 · Tailwind 3 ·
Flutter 3. See `backend/requirements.txt`, `frontend/package.json`, `mobile/pubspec.yaml`.

## Repository structure
```
backend/   app/** (API, auth, DB, engine, OCR interface), tests/** (49 tests)
frontend/  React portal   mobile/  Flutter app   samples/  demo label
docs/      10 guides + imported verification reports   team/  6 member files
setup.sh / setup.bat / start_demo.sh / start_demo.bat   verified scripts
```

## How to run
```bash
./setup.sh && ./start_demo.sh
# Web: http://127.0.0.1:5173 · API docs: http://127.0.0.1:8000/docs
# Login: LMO-DEL-2024-884 / 8842 (demo credentials)
```
Full guide: `RUN_PROJECT.md`. Backend tests: `cd backend && python -m unittest
discover -s tests -v` → **49 passed, 0 failed** (SQLite and PostgreSQL 18.6).

## How the six members collaborate
| Member | Owns | Key files |
|---|---|---|
| 1 — AI/OCR | Model + extraction quality | `backend/app/services/ai_ocr.py`, `samples/` |
| 2 — Legal | Verified rule content | `backend/app/2ndMember.json` |
| 3 — Backend | API, DB, engine, evidence, tests, contracts | `backend/app/**`, `backend/tests/**` |
| 4 — Flutter | Field mobile app | `mobile/**` |
| 5 — Web | Inspector portal | `frontend/**` |
| 6 — Integration/QA/Deploy | Setup, QA gate, security, hosting | `setup.*`, `RUN_PROJECT.md`, env |
Details: `team/member1.md` … `team/member6.md`, `docs/TEAM_RESPONSIBILITIES.md`.

## Current limitations (honest)
Demo officer PINs are hardcoded; read endpoints are unauthenticated in this MVP;
no rate limiting/HTTPS yet; Flutter multi-panel flow pending; `npm run build` and
`flutter analyze` need SDK-equipped machines. Full board: `PROJECT_STATUS.md`.

## Docs & audit
Start with `docs/PROJECT_OVERVIEW.md`, then `docs/ARCHITECTURE.md`,
`docs/API_GUIDE.md`. Upload safety: `GITHUB_UPLOAD_AUDIT.md` lists every included
and excluded file with reasons — no secrets are committed (`.env.example` only).
