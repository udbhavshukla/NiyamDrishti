# Run Project (fresh Mac)

All commands below are taken from the verified `setup.sh` / `start_demo.sh` scripts
and the test reports in `docs/`. Nothing here is invented.

## 1. Prerequisites / required software
| Need | Verified note |
|---|---|
| macOS (guide written for Mac) | Verified on macOS 26.6.2 (arm64) |
| Python 3.10+ | Verified with Python 3.13.15; repo README notes 3.11/3.12/3.14 tested |
| pip | Ships with Python (`pip3 --version` to check) |
| Node.js 18+ + npm | **Optional for backend; required for React frontend.** Not installed in the verification env — `setup.sh` skips gracefully with a note |
| Flutter SDK `>=3.0.0 <4.0.0` | **Only for the mobile app** (`mobile/pubspec.yaml`). Not installed in the verification env |
| PostgreSQL 14+ | **Optional.** Verified with PostgreSQL 18.6 (Postgres.app). Without it the backend runs on SQLite automatically |

## 2. One-command setup (recommended)
```bash
./setup.sh
```
What it does (from the script itself):
1. Creates `backend/venv` (`python3 -m venv venv`) and activates it.
2. `pip install -r requirements.txt` inside `backend/`.
3. Initializes the DB: `python -c "from app.database import create_tables; from app.seed_rules import seed_rules; create_tables(); seed_rules() ..."`.
4. `npm install` inside `frontend/` (skipped with a note if npm is missing).

Windows: run `setup.bat` instead (same four steps).

## 3. Environment variables
```bash
cp .env.example backend/.env   # or export them in your shell
```
| Variable | Required? | Effect |
|---|---|---|
| `AUTH_SECRET_KEY` | **Yes** | Without it login returns 500 and guarded routes 401 (fail-closed by design). Generate: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `DATABASE_URL` | No | Unset -> SQLite (`niyamdrishti.db`). For Postgres: `postgresql://USER@localhost:5432/niyamdrishti` |
| `CORS_ORIGINS` | No | Defaults cover `localhost:5173` + `localhost:3000` (+ 127.0.0.1). Comma-separated |
| `HOST` / `PORT` | No | Defaults `0.0.0.0` / `8000` |
| `EVIDENCE_STORAGE_PATH` | No | Defaults `./uploads/evidence` |

PostgreSQL setup (optional): `createdb niyamdrishti`, then
`export DATABASE_URL="postgresql://YOURUSER@localhost:5432/niyamdrishti"`.
Tables + 15 rules are created automatically on startup.

## 4. Start everything (demo)
```bash
./start_demo.sh
```
- Backend: `http://127.0.0.1:8000` (Swagger: `http://127.0.0.1:8000/docs`)
- Frontend: `http://127.0.0.1:5173`
- Login: officer `LMO-DEL-2024-884`, PIN `8842` (demo credentials)

Manual backend start: `cd backend && source venv/bin/activate && export PYTHONPATH=. && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
Manual frontend start: `cd frontend && npm run dev -- --host 127.0.0.1 --port 5173`.
Flutter app: open `mobile/` in Flutter tooling, set the API base URL in
`mobile/lib/api_service.dart`, run on emulator/device.

## 5. Test the backend
```bash
cd backend && source venv/bin/activate && export PYTHONPATH=.
python -m unittest discover -s tests -v     # expect: 49 tests, OK
```
With PostgreSQL: prefix `DATABASE_URL="postgresql://USER@localhost:5432/niyamdrishti"`.
Try a scan: log in via `/docs`, then `POST /inspection/quick-scan` with
`samples/label.jpg` attached. Fetch evidence via the returned `evidence_url` with
`?token=<your-token>` appended.

## 6. Common errors and fixes (all observed during verification)
| Symptom | Cause / fix |
|---|---|
| Login returns 500 `server_configuration` | `AUTH_SECRET_KEY` not set — export it (see §3) |
| Guarded endpoints return 401 | Missing/expired `Authorization: Bearer` header — log in again |
| Upload returns 400 `invalid_image_file` / `empty_file` | By design: send a real non-empty image |
| Evidence URL returns 401 in browser | Append `?token=<token>` (plain `<img>` can't send headers) |
| `npm: command not found` | Install Node 18+; backend still works without it |
| EasyOCR tries to download models | Offline default disables downloads; set `EASYOCR_DOWNLOAD=1` only if you want them |
| Port already in use | Another server on :8000/:5173 — stop it or change ports |
