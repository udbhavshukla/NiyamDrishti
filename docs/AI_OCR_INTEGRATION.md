# AI / OCR Integration

## Contract
`backend/app/services/ai_ocr.py :: analyze_package_label(image_bytes) -> dict`.
OCR is an extraction stage: it returns facts, never verdicts.

## Pipeline stages
1. **Decode** bytes via Pillow; undecodable input raises `ValueError` (mapped to
   HTTP 400 `invalid_image_file` — never a 500).
2. **Quality gate** (`check_image_quality`): blur (Laplacian variance),
   brightness, contrast, minimum 200x200 px. Issues are reported, not hidden.
3. **Preprocessing** (dedicated copy): downscale cap, deskew, CLAHE contrast,
   non-local-means denoise.
4. **OCR cascade** (`run_ocr`): EasyOCR (lazy import, download only if
   `EASYOCR_DOWNLOAD=1`) -> Tesseract (`pytesseract`, if installed) -> realistic
   offline simulator. Return value always names the engine used.
5. **Context-aware extraction**: MRP / net-quantity proximity matching, MFG-vs-expiry
   mutual exclusion, manufacturer + multi-line address (pincode stop), consumer-care
   phone/email, country of origin, prominent product-name heuristic.
6. **Review decision**: missing mandatory fields, quality issues, or average OCR
   confidence < 70% set `review_required` with human-readable reasons.

## Output shape (consumed by Member 3's engine)
9 canonical declaration slots — `product_name`, `net_quantity`, `mrp`,
`manufacturer`, `address`, `manufacturing_date`, `expiry_date`, `consumer_care`,
`country_of_origin` — each `{value, confidence, bbox, source, source_line}`,
plus `quality_metrics`, `ocr_engine`, `ocr_confidence_percent`, `raw_text`,
`ocr_lines`, `missing_mandatory`, `review_required`, `review_reasons`.

## Status notes (honest)
- The bundled pipeline runs real preprocessing + real OCR engines when installed;
  the simulator keeps the backend demo-able offline and always self-reports.
- Model accuracy work (engines, weights, languages) belongs to Member 1; the
  interface and fallbacks belong to the integration this file provides.
- Heavy deps (`torch`, `torchvision`, `easyocr`) are listed in
  `backend/requirements.txt` but imported lazily — CPU-only laptop setup works.
