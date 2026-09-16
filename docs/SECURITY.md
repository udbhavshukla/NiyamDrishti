# Security

## Implemented (verified in code + tests)
- **Fail-closed secret:** `AUTH_SECRET_KEY` is read from the environment on every use
  (`backend/app/auth.py`); no default exists. Missing secret -> login 500, guarded
  endpoints 401. Dedicated regression test included.
- **Token design:** `payload.signature` with HMAC-SHA256, 7-day expiry, constant-time
  signature and PIN comparison. PINs stored as SHA-256 hashes (demo credentials only).
- **Auth coverage:** `require_auth` guards all mutating inspection endpoints,
  `/auth/me`, and evidence retrieval. Recorded officer identity always comes from the
  token, ignoring spoofed body fields (tested).
- **Evidence protection:** no open static mount; authenticated route only (Bearer or
  `?token=`); filename/ID whitelist regex; `commonpath` containment; server-generated
  filenames (`{panel}_{ts}_{uuid8}.{ext}`); traversal -> 404 (tested).
- **Upload safety:** MIME -> empty -> decodable validation before any disk write;
  quick-scan rolls back orphan records on rejection (tested).
- **CORS:** explicit origins via `CORS_ORIGINS` (comma-separated); credentials only
  when no `*` wildcard is configured (tested).

## Demo credentials (NOT secrets — publicly documented, replace before any pilot)
Officer IDs `LMO-DEL-2024-884` / `FSO-MH-001` / `DIR-CENTRAL-001` with PINs
`8842` / `1234` / `9999` are hardcoded demo logins (also mirrored in the frontend
offline fallback). They exist so judges can log in; they must be replaced with a
real officer store before any production use.

## Known gaps (Member 6 — do not present as done)
- No rate limiting, no HTTPS/TLS termination, no production JWT library rotation.
- Read endpoints (`GET /inspection/{id}`, `/inspections`, `/dashboard`, `/report`,
  `/rules*`) are currently unauthenticated; evidence and all mutations are protected.
-Secret hygiene: this clean copy ships placeholder-only `.env.example`. The original
  project's root example file contained a real-looking secret value and was
  deliberately NOT copied (see `GITHUB_UPLOAD_AUDIT.md`).
