# Database

## Engine selection (`backend/app/database.py`)
- Default (no env): `sqlite:///./niyamdrishti.db` — zero-config local dev and tests.
- Production/demo: set `DATABASE_URL`, e.g.
  `postgresql://udbhav@localhost:5432/niyamdrishti` (verified against PostgreSQL 18.6).
- `create_tables()` creates all tables on startup and safely adds the `is_ecommerce`
  column on existing installs. Sessions are per-request via `get_db()`.

## Tables (`backend/app/models.py`)
| Table | Key columns |
|---|---|
| `inspections` | `inspection_id` (unique, e.g. `INS-20260912-3f1a`), `product_name`, `inspector_id`, `inspection_date`, `rule_version`, `overall_status` (PASS/FAIL/REVIEW_REQUIRED/PENDING), `is_ecommerce` (bool, nullable), `confidence`, timestamps |
| `declarations` | `inspection_id` (FK), `field_name`, `value`, `confidence`, `bbox` (JSON string), `source` |
| `violations` | `inspection_id` (FK), `rule_id`, `field_name`, `severity`, `status` (open/…), `reason`, `evidence_image`, `bbox`, `extracted_text`, `confidence` |
| `reviews` | `inspection_id` (FK), `decision`, `comment`, `reviewed_at`, `reviewer_id` |
| `rules` | `rule_id`, `version`, `field_name`, `requirement_type`, `requirement`, `severity`, `explanation`, `source_reference`, `effective_from/to`, `active` |

Relationships: one inspection -> many declarations / violations / reviews
(`all, delete-orphan` cascades). Rules are standalone reference data.

## Seeding
`python -m app.seed_rules` (or startup hook, or `setup.sh`) inserts the 15 legal
rules idempotently — existing `rule_id`s are skipped, so re-runs insert 0 rows.

## Operational notes
- The local `niyamdrishti.db` and `uploads/evidence/*` are **generated artifacts** and
  are git-ignored in this clean copy (see `GITHUB_UPLOAD_AUDIT.md`).
- For PostgreSQL: `createdb niyamdrishti`, set `DATABASE_URL`, start the app — tables
  and rules are created automatically.
