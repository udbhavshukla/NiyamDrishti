# Member 1 — AI / OCR

## Responsibility
Develop and improve the OCR model and extraction quality: text recognition,
bounding boxes, per-field values and confidence scores for packaged-commodity labels.

## Exact files / folders related to this work
| Path | Role |
|---|---|
| `backend/app/services/ai_ocr.py` | Integration file Member 1's model plugs into. Entry point: `analyze_package_label(image_bytes) -> dict`. Contains quality gate, preprocessing, engine cascade, and regex/context extraction stage |
| `backend/app/schemas.py` (`OCRField`, `OCRDeclarationsPayload`) | The output contract the OCR stage must satisfy: `field_name -> {value, confidence, bbox, source}` |
| `backend/tests/test_integration_ai.py` | 9 integration tests covering the OCR pipeline + analyze path |
| `samples/label.jpg` | Reference label image for manual OCR checks |

## Important APIs / components
- `analyze_package_label(image_bytes)` returns: `quality_metrics`, `ocr_engine`,
  `ocr_confidence_percent`, `raw_text`, `ocr_lines`, `declarations` (9 canonical fields:
  `product_name`, `net_quantity`, `mrp`, `manufacturer`, `address`,
  `manufacturing_date`, `expiry_date`, `consumer_care`, `country_of_origin`),
  `review_required`, `review_reasons`.
- Engine cascade inside `run_ocr()`: EasyOCR (if installed) -> Tesseract (if installed)
  -> realistic offline simulator. The returned `ocr_engine` string always says which ran.
- Quality gate (`check_image_quality`): blur (Laplacian variance), brightness, contrast,
  minimum dimensions. Failures become `review_reasons`, never silent passes.

## Dependencies on other members
- **Member 3 (backend):** owns `ai_ocr.py` as an integration file, the `OCRField`
  contract, and the rule engine that consumes OCR facts. Coordinate before changing the
  `declarations` dict shape — the rule engine's `FIELD_ALIASES` and `/analyze` endpoint
  depend on it.
- **Member 2 (legal):** the 9 canonical field names map to rule `field_name` values.
  New legal fields require a matching extraction slot.

## What to understand before modifying code
1. Confidence is an AI-quality signal only — it is never a legal threshold. The rule
   engine (Member 3) routes low confidence to `REVIEW_REQUIRED`, never auto-FAIL.
2. Heavy ML deps (`torch`, `easyocr` in `backend/requirements.txt`) are optional at
   runtime because of lazy imports + fallbacks. Do not make them hard imports.
3. The offline simulator exists so the backend stays demo-able without internet.
   Improve the real engines; keep the fallback honest (it reports `simulated_offline`).
