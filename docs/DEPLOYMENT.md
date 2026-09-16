# Deployment

## Current state: local demo + verified test gate (not production)
The system runs as two local processes (`start_demo.sh`): FastAPI on `:8000`,
Vite React dev server on `:5173`. The Flutter app talks to the backend over HTTP.

## Production checklist (Member 6)
1. **Environment:** set `DATABASE_URL` (PostgreSQL), strong `AUTH_SECRET_KEY`
   (generate: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`),
   explicit `CORS_ORIGINS`, `HOST`/`PORT`. Never commit `.env`.
2. **Backend:** ASGI server (uvicorn/gunicorn) behind TLS-terminating reverse proxy;
   run `create_tables()` + `seed_rules()` once; serve `uploads/evidence/` only through
   the authenticated route (never a static mount).
3. **Frontend:** `npm run build`, host the static bundle, set `VITE_API_BASE_URL`.
4. **Mobile:** point `api_service.dart` at the public API base URL; release-sign builds.
5. **Hardening first:** add rate limiting, HTTPS everywhere, replace demo officer
   credentials with a real store, authenticate read endpoints as policy requires,
   rotate to a standard JWT library with key rotation.
6. **CI gate:** backend `python -m unittest discover -s tests` (49/49) on every PR,
   plus `npm run build` and `flutter analyze` once those SDKs are in CI.

## What NOT to do
- Do not deploy with SQLite, demo PINs, `CORS_ORIGINS=*`, or the placeholder secret.
- Do not version-control `.env`, `*.db`, `uploads/evidence/*`, or model weight
  downloads — all are git-ignored here.
