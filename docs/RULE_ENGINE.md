# Rule Engine

Source: `backend/app/services/rule_engine.py` (+ `rule_version_resolver.py`).
Principle (from the module docstring): OCR/AI supplies facts and confidence; this
module evaluates those facts using only the rule records selected by the version
resolver. It never creates legal requirements and never asks an LLM for a verdict.

## Inputs / outputs
- Input: `{field_name: OCRField(value, confidence, bbox, source)}`, the resolved
  `rules` list, `rule_version`, `is_ecommerce` context.
- Output: `{overall_status, rule_version, checks[], violations[], warnings[]}`.
  Each check: `{rule_id, field, status, value, confidence, reason}`.

## Requirement types (`_evaluate_requirement`)
| Type | Behavior |
|---|---|
| `required` / `mandatory_declaration` | present -> PASS, missing -> FAIL |
| `pattern` | regex full-match -> PASS else FAIL; invalid stored regex -> REVIEW_REQUIRED |
| `equals` | case-insensitive equality |
| `prohibition` | REVIEW_REQUIRED (needs physical label check, e.g. stickers / over-MRP) |
| `format_requirement` | REVIEW_REQUIRED (needs measurement: numeral height, language) |
| `conditional_exemption` / `scope_limit` | PASS, noted |
| unknown | REVIEW_REQUIRED — never guessed |

## Gates applied before evaluation
1. **Legal gate:** rules without a real `source_reference` (or marked
   `LEGAL SOURCE VERIFICATION REQUIRED`) yield REVIEW_REQUIRED, never PASS/FAIL.
2. **E-commerce scoping:** fields starting with `ECOMMERCE_` apply only when
   `is_ecommerce is True`; `False` -> NOT_APPLICABLE; `None` -> REVIEW_REQUIRED.
3. **Confidence zones:** missing/< 0.60 -> REVIEW_REQUIRED; 0.60–0.89 review zone ->
   REVIEW_REQUIRED; >= 0.90 -> engine decides. Confidence never causes FAIL.
4. **Field aliasing:** exact -> case-insensitive -> alias map (`FIELD_ALIASES`) ->
   reverse-alias lookup.

## Overall status
`FAIL` if any check FAILs; else `REVIEW_REQUIRED` if any check needs review; else `PASS`.
Same facts + same rule version -> same verdict, every run (deterministic).

## Current rule dataset
15 records seeded by `backend/app/seed_rules.py` from `backend/app/2ndMember.json`
(rule IDs match exactly — verified during audit). Do not invent or edit rule text
without Member 2 legal review.
