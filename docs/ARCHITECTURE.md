# Architecture

## Runtime topology (demo)
```
Flutter app (Member 4) ──┐
                         ├──> FastAPI :8000 ──> SQLite (default) / PostgreSQL (DATABASE_URL)
React portal :3000 (Member 5) ──┘                        │
                                                         └── uploads/evidence/<inspection_id>/
```
The web and mobile clients only talk to the backend over HTTP. There is no direct
DB access from any client and no client-to-client communication.

## Backend module map (`backend/app/`)
| File | Responsibility |
|---|---|
| `main.py` | FastAPI app, all 14 routes, request handling, panel merge, persistence |
| `auth.py` | Officer registry, HMAC-SHA256 token create/verify, `require_auth` |
| `database.py` | Engine + sessions; `create_tables()` auto-creates schema |
| `models.py` | ORM: `Inspection`, `Declaration`, `Violation`, `Review`, `Rule` |
| `schemas.py` | Pydantic contracts (`CreateInspectionRequest`, `OCRField`, `AnalyzeInspectionResponse`, dashboards, reports…) |
| `seed_rules.py` | Idempotent insert of the 15 legal rules |
| `services/ai_ocr.py` | Quality gate -> preprocessing -> OCR -> 9-field extraction |
| `services/rule_engine.py` | Deterministic evaluation of facts vs one rule version |
| `services/rule_version_resolver.py` | Picks the active version from DB rows |
| `2ndMember.json` | Legal source dataset (Member 2), preserved verbatim |

## Data flow for one scan
`POST /inspection/quick-scan` (or create + `/evidence` per panel):
validate image -> `analyze_package_label()` -> merge with stored panels
(higher confidence wins per field) -> `get_current_rules()` -> `evaluate_rules()`
-> persist declarations + violations -> update `overall_status`/`rule_version`/
`confidence` -> respond with checks, violations, OCR metrics, evidence URL.

## Key design decisions
1. **Rules live in rows, not code.** Law changes = data change (+ re-seed), not redeploy.
2. **AI reads; rules decide.** OCR output is facts + confidence; compliance verdicts
   come only from the engine + officer review.
3. **Humans are in the loop by schema.** `REVIEWS` rows are append-only and survive
   re-analysis; uncertain engine output is `REVIEW_REQUIRED`, never a guess.
4. **Evidence is a first-class citizen.** Every violation can carry `evidence_image` +
   `bbox`; files are served only to authenticated officers.
