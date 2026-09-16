# NiyamDrishti AI — Member 3 BUG FIX REPORT

**Date:** 2026-09-11 (final verification re-run)
**Team role:** Member 3 (Backend + DB + Rule Engine + AI Integration)
**Scope:** BUG-001 → BUG-009 review; BUG-002, BUG-003, BUG-007, BUG-009 fixed (BUG-001 verified fixed).
**Final status:** 49/49 tests pass on SQLite AND PostgreSQL; live verification in `FINAL_TEST_REPORT.md`.

---

## Summary

| Bug ID | Title | Status |
|--------|-------|--------|
| BUG-001 | `setup.sh`/`setup.bat`/README import `seed_rules` without the `app.` package prefix | ✅ VERIFIED FIXED (already correct) |
| BUG-002 | Analysis reports `FAIL` for e-commerce-only rules on every physical scan | ✅ FIXED |
| BUG-003 | Corrupt / non-image uploads are written to disk before validation and create orphaned inspections | ✅ FIXED |
| BUG-007 | `AUTH_SECRET_KEY` has a hardcoded fallback in source code | ✅ FIXED |
| BUG-009 | Inspection evidence is served as public static assets without authentication | ✅ FIXED |

---

## BUG-001 — setup scripts import `seed_rules` without `app.` prefix

**Reported concern:** `setup.sh`, `setup.bat`, and `README.md` ran `python -m seed_rules`
instead of `python -m app.seed_rules`, so rule seeding failed with `ModuleNotFoundError`.

**Root cause:** The seed module lives at `app/seed_rules.py`; the setup documents referenced it
without the package prefix.

**Fix applied:** None required — verified all three locations already use `app.seed_rules`:
- `setup.sh`: `python3 -m app.seed_rules`
- `setup.bat`: `python -m app.seed_rules`
- `README.md`: `python -m app.seed_rules`

**Files changed:** — (already correct)

**How verified:** `grep` over `setup.sh`, `setup.bat`, `README.md`; no `seed_rules` reference lacks the `app.` prefix.

---

## BUG-002 — E-commerce-only rules fire `FAIL` on physical (retail) scans

**Reported concern:** On a physical product inspection, missing/non-applicable "online / e-commerce
listing" fields produced `FAIL` violations (e.g. `LM-PC-006-10A-COO-2026`), even though those
requirements apply only to India e-commerce platforms.

**Root cause:** The deterministic rule engine evaluated every rule uniformly. Rules whose
`field_name` denotes an e-commerce requirement were not scoped; absence of the e-commerce-only
fields on a physical label therefore evaluated as a hard `FAIL`.

**Fix applied — e-commerce scoping:**
- `app/services/rule_engine.py`:
  - New constant `ECOMMERCE_FIELD_PREFIX = "ECOMMERCE_"`.
  - `evaluate_rules(..., is_ecommerce: bool | None = None)` threads the context into every check.
  - Rules with an `ECOMMERCE_` field are handled by context:
    - `is_ecommerce=False` → `NOT_APPLICABLE` (skipped; never a violation).
    - `is_ecommerce=None` (unknown) → `REVIEW_REQUIRED` (human confirms the channel; never a hard FAIL).
    - `is_ecommerce=True` → evaluated normally (PASS/FAIL/REVIEW_REQUIRED).
- `app/schemas.py`:
  - `CreateInspectionRequest.is_ecommerce: Optional[bool] = None` (defaults False at create).
  - `AnalysisCheck.status` pattern extended to `^(PASS|FAIL|REVIEW_REQUIRED|NOT_APPLICABLE)$`.
  - `AnalyzeInspectionResponse.is_ecommerce`.
- `app/main.py`:
  - `POST /inspection`, `/inspection/quick-scan`, `/{id}/evidence`, `/{id}/analyze` accept/thread
    `is_ecommerce` (body or `?is_ecommerce=` query).
  - `Inspection.is_ecommerce` persisted (model column added; DB column `is_ecommerce`, default false).

**Files changed:** `app/services/rule_engine.py`, `app/schemas.py`, `app/main.py`, `app/models.py`
(existing column).

**How verified:**
- Live (curl, physical quick-scan): `overall_status` no longer FALSE-fails; e-commerce checks return
  `NOT_APPLICABLE`; violations list empty for e-commerce rules.
- Live (analyze with `is_ecommerce=true` on listing with MRP but no COO): `ECOMMERCE_COUNTRY_OF_ORIGIN_FILTER`
  and `ECOMMERCE_LISTING_DECLARATIONS` correctly `FAIL`.
- Unit (engine): NOT_APPLICABLE / REVIEW_REQUIRED / FAIL / PASS paths asserted in
  `tests/test_bugfix_regressions.py` → `EcommerceScopingTests` (5 tests).

---

## BUG-003 — Invalid image uploads written to disk + orphaned inspections

**Reported concern:** Corrupt or non-image files were persisted to the evidence directory and a
`PENDING` inspection was created before analysis could fail.

**Root cause:** Uploaded bytes were written to disk (and an inspection row committed) before any
validation; failure during decoding was not caught, so an orphaned `PENDING` inspection remained.

**Fix applied:**
- `app/main.py` `upload_inspection_evidence` now validates **in memory** before any disk I/O:
  - `Content-Type` not `image/*` → **HTTP 400** `{"detail": {"error": "invalid_image_file", ...}}`.
  - Empty file → **HTTP 400** (same error code).
  - `analyze_package_label` `ValueError` (decoding failure) → **HTTP 400** `{"detail": {"error": "invalid_image_file", ...}}`.
- `app/main.py` `quick_scan_inspection` wraps its inner evidence upload; when the upload returns
  HTTP 400 it deletes the just-created `PENDING` inspection and commits, so no orphaned records remain.
- Files are written only after successful validation; filenames are server-generated.

**Files changed:** `app/main.py`.

**How verified:**
- Live (curl): quick-scan with `requirements.txt` (`text/plain`) → HTTP 400 with
  `{"detail":{"error":"invalid_image_file","message":"Uploaded file is not an image."}}`; a corrupt
  file → HTTP 400; empty file → HTTP 400.
- Dashboard total unchanged after a rejected quick-scan (no orphan `PENDING`).
- Automated: `tests/test_bugfix_regressions.py` → `InvalidImageUploadTests` (5 tests: quick-scan corrupt +
  no-orphan assertion, empty, evidence corrupt, non-image MIME, valid image → 200).

---

## BUG-007 — `AUTH_SECRET_KEY` hardcoded fallback in source

**Reported concern:** A default hardcoded secret existed in the auth code, so deployments that forgot to
set `AUTH_SECRET_KEY` still "worked" with a public secret.

**Root cause:** `auth.py` initialized `SECRET_KEY = os.environ.get("AUTH_SECRET_KEY", "<hardcoded>")`
at import time.

**Fix applied — fail closed:**
- `app/auth.py`:
  - Removed the hardcoded fallback constant entirely.
  - `_get_secret_key()` reads `os.environ.get("AUTH_SECRET_KEY")` on every call (no module-level cache).
  - `create_token()` raises `HTTPException(500)` when the secret is missing (login cannot proceed).
  - `verify_token()` returns `None` when the secret is missing (every request → 401).
  - `get_current_officer()` / `require_auth` → **HTTP 401** when no valid bearer token.

**Files changed:** `app/auth.py`.

**How verified:**
- Unit: `tests/test_bugfix_regressions.py` → `MissingSecretFailClosedTests` asserts `/auth/login` → 500
  and `POST /inspection` → 401 when the env var is cleared mid-process.
- Live: server started **without** `AUTH_SECRET_KEY` → login 500, protected route 401; started with a
  secret → login 200 + protected route succeeds.

---

## BUG-009 — Evidence exposed as unauthenticated static files

**Reported concern:** `/uploads/evidence/...` was mounted as a public `StaticFiles` path, so anyone with
the URL could download evidence images with no authentication, and `..`/filename tricks were not guarded.

**Root cause:** `app/main.py` used `app.mount("/uploads", StaticFiles(directory=...))`, bypassing all auth
and serving arbitrary nested paths.

**Fix applied:**
- `app/main.py`:
  - Removed the `StaticFiles` mount on `/uploads` entirely.
  - New authenticated route `GET /uploads/evidence/{inspection_id}/{filename}`:
    - Auth by `Authorization: Bearer <token>` or `?token=<token>` (query param keeps `<img>` tags working).
    - Filename regex whitelist `[A-Za-z0-9!()@._-]+`; any other character (e.g. `..`, `/`, `%00`) → **HTTP 400**.
    - `os.path.commonpath` containment check against `EVIDENCE_DIR` → traversal → **HTTP 400/404**.
    - Returns `FileResponse`; **401** unauthenticated, **404** missing.
  - `_safe_evidence_filename()` generates filenames server-side: `{panel_type}_{timestamp}_{uuid}.{ext}` —
    client-supplied filenames are never used on disk.

**Files changed:** `app/main.py`, `frontend/src/api.js` (appends `?token=` to evidence URLs for `<img>` tags).

**How verified:**
- Live (curl): evidence URL without auth → 401; with `?token=` → 200 image bytes; with Bearer header → 200;
  `..%2F..%2Fniyamdrishti.db` traversal attempt → 404; upload of `filename=../../../../etc/passwd.jpg`
  stored as `primary_<timestamp>_<uuid>.jpg` (client filename discarded).
- Automated: `tests/test_bugfix_regressions.py` → `EvidenceSecurityTests` (4 tests: 401 unauthenticated,
  200 with Bearer, 200 with `?token=`, traversal rejected at the function level).

---

## Regression Coverage

New file `backend/tests/test_bugfix_regressions.py` (25 tests) added to lock in the fixes:

| Test class | Area | Tests |
|------------|------|-------|
| `EcommerceScopingTests` | BUG-002 engine behavior | 5 |
| `AuthGuardTests` | BUG-007 401s + token identity | 7 |
| `InvalidImageUploadTests` | BUG-003 400s + no-orphan | 5 |
| `CorsTests` | explicit origin + disallowed origin | 2 |
| `MissingSecretFailClosedTests` | BUG-007 fail-closed | 1 |
| `EvidenceSecurityTests` | BUG-009 auth + traversal | 4 |
| `MultiPanelMergeTests` | multi-panel accumulate + no duplicates | 1 |
| `QuickScanOrphanCleanupTests` *(see InvalidImageUploadTests)* | BUG-003 | — |

**Full suite:** `python3 -m unittest discover -s tests` → **49 tests, 0 failures, 0 errors** on both
SQLite and PostgreSQL (2026-09-11). Live end-to-end verification of every fix is recorded in
`FINAL_TEST_REPORT.md`.

## Additional Fix Found During Final Verification (2026-09-11)

- **SQLAlchemy identity-map `SAWarning`** on multi-panel merge: bulk deletes with
  `synchronize_session=False` left stale loaded rows in the session identity map; SQLite's rowid
  reuse then collided when new rows were flushed.
- Fix: `db.expunge(stale)` each loaded declaration after the delete, before inserting the merged set
  (`app/main.py`). PostgreSQL (sequence PKs) was never affected, but the verbose SQLite run is now
  warning-free.

## Remaining Issues (deferred to Member 6)

1. Rate limiting / request size limits.
2. HTTPS in production.
3. Deployment config.
4. Optional: extend generic evaluator to Member 2 requirement types (`prohibition`, `format_requirement`,
   etc.) — currently `REVIEW_REQUIRED` by design.