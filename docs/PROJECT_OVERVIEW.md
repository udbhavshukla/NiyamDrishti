# Project Overview — NiyamDrishti AI

## What it is
NiyamDrishti AI is an AI-assisted inspection platform for **Legal Metrology Officers
(LMOs)** under the Department of Consumer Affairs, Government of India. An officer
photographs a pre-packaged commodity label; the system extracts the statutory
declarations with OCR and evaluates them against versioned Legal Metrology
(Packaged Commodities) Rules, 2011 requirements, producing an explained,
human-reviewed verdict.

## Problem being solved
Manual label inspections are slow, inconsistent across officers, and hard to audit.
Online (e-commerce) listings add a second surface — Rule 6(10)/6(10A) digital-listing
duties — that physical-only checks miss or mis-apply (see BUG-002 in
`BUG_FIX_REPORT.md`).

## Target users
- Field Legal Metrology Officers (Flutter mobile app).
- Desk/circle officers and reviewers (React web portal).
- Legal team (rule data stewardship) and enforcement command (dashboards, reports).

## How the pieces fit (60 seconds)
1. **Capture** (Member 4 Flutter / Member 5 React) — photo of the label panel(s).
2. **Extract** (Member 1 OCR via `backend/app/services/ai_ocr.py`) — 9 canonical
   fields with value + confidence + bounding box.
3. **Resolve** (`rule_version_resolver.py`) — active rule version from the database.
4. **Decide** (`rule_engine.py`) — deterministic PASS / FAIL / REVIEW_REQUIRED /
   NOT_APPLICABLE per rule; violations stored with evidence.
5. **Review** (`POST /inspection/{id}/review`) — officer confirms or overrides.
6. **Report** (`GET /dashboard`, `GET /inspection/{id}/report`) — stats + full record.

## Technology stack (actual, from `backend/requirements.txt`, `package.json`, `pubspec.yaml`)
| Layer | Tech |
|---|---|
| API | FastAPI, Uvicorn, Pydantic v2, python-multipart |
| Database | SQLAlchemy 2 + SQLite (default) / PostgreSQL 18 (production) |
| Vision | OpenCV (headless), Pillow, NumPy; EasyOCR primary, Tesseract fallback, offline simulator |
| Web | React 18, Vite 6, react-router-dom 6, Tailwind CSS 3 |
| Mobile | Flutter 3 (`http`, `image_picker`) |

## Repository layout (this clean copy preserves the real architecture)
```
backend/    FastAPI app + tests + requirements
frontend/   React inspector portal
mobile/     Flutter inspector app (temp mock_api.dart excluded — see audit)
samples/    Demo label image
docs/       This documentation + imported verification reports
team/       Per-member responsibility files
setup.sh / setup.bat / start_demo.sh / start_demo.bat   Verified run scripts
```

## Status snapshot
- Backend: **49/49 automated tests pass** on SQLite and PostgreSQL 18.6
  (evidence: `FINAL_TEST_REPORT.md`).
- Frontend/mobile: functional code present; Node and Flutter SDKs were unavailable in
  the verification environment, so `npm run build` / `flutter analyze` were not
  re-verified here — see `PROJECT_STATUS.md`.
