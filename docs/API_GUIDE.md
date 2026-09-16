# API Guide

Base URL (local demo): `http://127.0.0.1:8000`. Interactive docs: `GET /docs`.
Auth: `Authorization: Bearer <token>` from `POST /auth/login`
(demo officer `LMO-DEL-2024-884` / PIN `8842` — demo credentials only).

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | No | Liveness probe (`{"status":"ok","version":"1.0.0"}`) |
| POST | `/auth/login` | No | `{officer_id, pin}` -> `access_token` + officer profile |
| GET | `/auth/me` | Yes | Current officer profile |
| POST | `/inspection` | Yes | Create inspection (`{product_name, inspector_id?, is_ecommerce?}`) -> 201 PENDING |
| GET | `/inspection/{id}` | No | Full detail incl. declarations, violations, reviews |
| GET | `/rules` | No | List stored rules (`?active=true/false`) |
| GET | `/rules/current` | No | Active version + its rules |
| POST | `/inspection/{id}/analyze` | Yes | Body = `{field: {value, confidence?, bbox?, source?}}`; query `is_ecommerce?`; runs engine |
| POST | `/inspection/{id}/evidence` | Yes | Multipart `file` + `?panel_type=&is_ecommerce?`; OCR + merge + evaluate |
| POST | `/inspection/quick-scan` | Yes | One-shot create + upload + evaluate |
| POST | `/inspection/{id}/review` | Yes | `{decision: PASS\|FAIL\|REVIEW_REQUIRED, comment?}` |
| GET | `/inspections` | No | Paginated list (`page`, `page_size`, `status`) |
| GET | `/dashboard` | No | Counts + recent inspections |
| GET | `/inspection/{id}/report` | No | Full report payload |
| GET | `/uploads/evidence/{id}/{file}` | Yes (header or `?token=`) | Serve evidence photo |

## Notes that matter for integrators
- Error bodies are shaped `{"detail": {"error": "<code>", "message": "..."}}`.
  Image errors: `invalid_image_file` (wrong MIME / undecodable bytes),
  `empty_file` (zero bytes). Auth errors: `unauthorized`, `invalid_credentials`.
- `panel_type` is a **query** parameter (`primary|mrp|manufacturer|back|front|other`).
- `is_ecommerce`: `false` = physical (e-commerce rules -> `NOT_APPLICABLE`),
  `true` = digital listing (evaluated), omitted/`null` = unknown (`REVIEW_REQUIRED`).
- Recorded `inspector_id`/`reviewer_id` always come from the token, even if the body
  contains those fields.
- Evidence `<img>` usage: append `?token=<token>` (see `frontend/src/api.js`
  `evidenceImageUrl`).
