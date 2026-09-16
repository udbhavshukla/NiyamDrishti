# Member 2 — Legal Research & Verified Legal Rules / Data

## Responsibility
Research the Legal Metrology (Packaged Commodities) Rules, 2011 (as amended) and
supply verified, versioned rule records. No code changes are needed to change the law
as applied by the system — only database rows.

## Exact files / folders related to this work
| Path | Role |
|---|---|
| `backend/app/2ndMember.json` | **Source dataset**: Member 2's verified rule set (`_dataset_notes` + `rules`, 15 rule records). Legal source of truth, preserved verbatim — do not edit without legal review |
| `backend/app/seed_rules.py` | Loader (written by Member 3) that inserts the 15 rules idempotently; rule IDs here match `2ndMember.json` exactly |
| `backend/app/models.py` (`Rule`) | Storage shape: `rule_id`, `version`, `field_name`, `requirement_type`, `requirement`, `severity`, `explanation`, `source_reference`, `effective_from/to`, `active` |

## Important APIs / components
- `GET /rules` and `GET /rules/current` expose the stored rules.
- `app/services/rule_version_resolver.py` selects the active version purely from
  `active` + `effective_from/to` columns. It contains no rule IDs or dates.
- Live version-switch example already stored: `LM-PC-006-10A-COO-2026` (active
  2026-07-01 → 2027-06-30) vs `LM-PC-006-10A-COO-2027` (`active = False`, effective
  2027-07-01). Flipping one boolean switches versions with no redeploy.

## Dependencies on other members
- **Member 3 (backend):** owns the seeder, resolver, and engine. To add/change a rule,
  give Member 3 the record fields above; Member 3 re-runs `seed_rules()`.
- **Member 1 (AI/OCR):** new `field_name` values need a matching OCR extraction slot.

## What to understand before modifying data
1. Every rule MUST carry a real `source_reference`. Rules marked
   `LEGAL SOURCE VERIFICATION REQUIRED` are never auto-applied — the engine forces
   `REVIEW_REQUIRED` (see `docs/FINAL_TEST_REPORT.md`, legal gate).
2. `requirement_type` vocabulary the engine understands: `required` /
   `mandatory_declaration`, `pattern`, `equals`, `prohibition`, `format_requirement`,
   `conditional_exemption`, `scope_limit`. Anything else routes to human review.
3. E-commerce-only rules MUST use an `ECOMMERCE_`-prefixed `field_name` so the engine
   scopes them to digital listings (BUG-002 fix — see `docs/BUG_FIX_REPORT.md`).
4. Never invent rule text: the 15 seeded IDs are the verified set.
