# Team Responsibilities (summary)

Full per-member files: `../team/member1.md` … `../team/member6.md`.
This page is the one-screen map; the member files are authoritative.

| Member | Owns | Touches (files) | Depends on |
|---|---|---|---|
| 1 — AI/OCR | OCR model quality, extraction accuracy | `backend/app/services/ai_ocr.py` (model side), `samples/label.jpg`, OCR-side of `test_integration_ai.py` | Member 3's `OCRField` contract; Member 2's field names |
| 2 — Legal | Verified rule content + versioning data | `backend/app/2ndMember.json` (source of truth), rule rows via seeder | Member 3 to seed/apply; Member 1 for field slots |
| 3 — Backend | API, DB, engine, resolver, evidence, review, tests, contracts | `backend/app/**`, `backend/tests/**`, `backend/requirements.txt` | Member 1 facts, Member 2 rules; serves 4/5/6 |
| 4 — Flutter | Field mobile app | `mobile/**` (minus excluded temp mock) | Member 3 API; Member 6 builds |
| 5 — Web | Inspector portal | `frontend/**` | Member 3 API; Member 6 builds |
| 6 — Integration/QA/Deploy | Setup, QA gate, security, hosting | `setup.*`, `start_demo.*`, `.env.example`, `.gitignore`, `RUN_PROJECT.md`, `PROJECT_STATUS.md` | All members' run/test commands |

## Collaboration rules
1. API contracts (`backend/app/schemas.py`, `docs/API_GUIDE.md`) change only with
   Members 3 + 4 + 5 in the loop.
2. Rule content changes go through Member 2; engine behavior changes go through
   Member 3; neither edits the other's layer.
3. OCR output-shape changes go through Members 1 + 3 together (engine aliases +
   `/analyze` depend on field names).
4. No real secrets in chat, docs, or code — placeholders only (see `docs/SECURITY.md`).
