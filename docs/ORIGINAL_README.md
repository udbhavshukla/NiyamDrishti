# NiyamDrishti AI (नियमदृष्टि)
### AI-Powered Legal Metrology Packaged Commodity Inspection Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.x-61DAFB.svg?logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6.x-646CFF.svg?logo=vite)](https://vitejs.dev)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B.svg?logo=flutter)](https://flutter.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Government%20of%20India-blue.svg)]()

---

## 1. Overview

**NiyamDrishti AI** is a specialized, production-grade regulatory enforcement and compliance verification platform built for **Legal Metrology Officers (LMOs)** under the **Department of Consumer Affairs, Government of India**.

The system automates the inspection of pre-packaged commodities against the statutory mandates of the **Legal Metrology (Packaged Commodities) Rules, 2011**, specifically:
- **Rule 6(1)**: Mandatory label declarations (Product Identity, Net Quantity, MRP, Manufacturer/Packer/Importer details, Dates, Consumer Care, Country of Origin).
- **Rule 5 & 18**: Net Quantity format, permissible metric units, non-deceptive packaging, and dual declaration rules.
- **Rule 6(1)(e)**: Strict MRP formatting (`₹` / `Rs.`, inclusive of all taxes, prohibiting multiple MRPs).
- **Rule 6(1)(d)**: Month & Year of manufacture/packing with strict exclusion of expiry/use-by confusion.
- **Rule 6(1)(a)**: Comprehensive manufacturer/packer contact details (name, complete address, pincode).
- **Rule 6(1)(f)**: Consumer grievance redressal mechanisms (toll-free phone, email, officer name).
- **Rule 6(10)**: E-commerce marketplace display disclosures.

---

## 2. System Architecture

```
                                  ┌───────────────────────────────┐
                                  │   Legal Metrology Inspector   │
                                  └───────────────┬───────────────┘
                                                  │
                 ┌────────────────────────────────┴────────────────────────────────┐
                 │                                                                 │
                 ▼                                                                 ▼
   ┌───────────────────────────────┐                             ┌─────────────────────────────────┐
   │    React Inspector Portal     │                             │      Flutter Inspector App      │
   │  (Desktop / Tablet Dashboard) │                             │   (Field Smartphone Handheld)   │
   │   - Officer Auth / Session    │                             │   - Guided multi-angle capture  │
   │   - Interactive Evidence View │                             │   - Auto-crop & on-device preview│
   │   - Rule violation overrides  │                             │   - Rapid field quick-scan      │
   │   - Notice generation & stats │                             │   - Offline graceful fallback   │
   └───────────────┬───────────────┘                             └────────────────┬────────────────┘
                   │                                                              │
                   │ REST API / JWT                                               │ Multipart HTTP
                   └──────────────────────────────┬───────────────────────────────┘
                                                  │
                                                  ▼
   ┌───────────────────────────────────────────────────────────────────────────────────────────────┐
   │                                FastAPI Enforcement Core (Port 8000)                           │
   ├───────────────────────────────────────────────────────────────────────────────────────────────┤
   │  Endpoints:                                                                                   │
   │    /auth/login, /auth/me       -> Inspector authentication & zone assignment                  │
   │    /inspection/quick-scan      -> Direct one-shot image evidence upload & AI analysis         │
   │    /inspection/{id}/evidence   -> Multi-panel evidence uploads (primary, mrp, details)        │
   │    /inspection/{id}/review     -> Statutory override & enforcement sign-off                   │
   │    /dashboard, /reports        -> Real-time inspection registries & regulatory analytics      │
   │    /rules/current              -> Versioned Legal Metrology rule lookup                       │
   ├───────────────────────────────────────────────────────────────────────────────────────────────┤
   │                                  Internal Pipeline Services                                   │
   │                                                                                               │
   │  1. Evidence Ingestion & Quality Gate (ai_ocr.py)                                             │
   │     • Blur detection (Laplacian variance >= 80.0)                                             │
   │     • Brightness check (mean gray 35.0 - 245.0)                                               │
   │     • Contrast check (std dev >= 20.0)                                                        │
   │     • Minimum dimensions (>= 300x300 px)                                                      │
   │                                                                                               │
   │  2. Computer Vision & Unified OCR Preprocessor                                                │
   │     • Grayscale conversion, CLAHE adaptive contrast, bilateral denoise, Otsu deskew          │
   │     • Primary: EasyOCR (PyTorch deep learning detection & CRNN recognition)                   │
   │     • Secondary / Fallback: Tesseract OCR + Simulated Offline Packaging Engine                │
   │                                                                                               │
   │  3. Spatial & Semantic Declaration Extraction                                                 │
   │     • Context-Proximity Matching: Constrained within 120 chars of statutory keywords          │
   │     • MFG vs. Expiry Separation: Strict line isolation preventing false cross-matching        │
   │     • Multi-Line Address & PIN Parsing: Detects registered office, works, PIN codes           │
   │     • Canonical Fact Normalization: Emits standard OCRField models with bounding boxes       │
   │                                                                                               │
   │  4. Deterministic Legal Metrology Rule Engine (rule_engine.py)                                │
   │     • 15 Member 2 Legal Metrology Rules version-controlled in database                       │
   │     • Requirement Types: mandatory_declaration, format_requirement, prohibition, etc.       │
   │     • Dual thresholding: high-confidence pass, low-confidence review routing, absence fail    │
   │     • Full statutory legal references (e.g. Rule 6(1)(d), Rule 6(1)(e), Rule 18)             │
   └──────────────────────────────┬────────────────────────────────┬───────────────────────────────┘
                                  │                                │
                                  ▼                                ▼
                 ┌────────────────────────────────┐ ┌──────────────────────────────┐
                 │     Database Layer             │ │    Evidence File Storage     │
                 │  - SQLite (niyamdrishti.db)    │ │   uploads/evidence/{id}/     │
                 │  - PostgreSQL (DATABASE_URL)   │ │   Timestamped panel files    │
                 │  - 15 Rules & Officers Seeded  │ │   Static mount: /uploads     │
                 └────────────────────────────────┘ └──────────────────────────────┘
```

---

## 3. Directory Layout

```
c:/finaal stage/
├── README.md                     # System documentation & quickstart (this file)
├── INTEGRATION_REPORT.md         # Comprehensive engineering audit & verification report
├── .env.example                  # Environment configuration template
│
├── backend/                      # Production FastAPI Backend & AI/OCR Service
│   ├── venv/                     # Python 3.11+ Virtual Environment
│   ├── niyamdrishti.db           # Zero-configuration SQLite database (auto-created & seeded)
│   ├── requirements.txt          # Production Python dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application, CORS, routers, startup hooks
│   │   ├── auth.py               # Officer JWT authentication & security registry
│   │   ├── database.py           # SQLite/PostgreSQL engine, session factory, Base
│   │   ├── models.py             # SQLAlchemy models (Inspections, Declarations, Violations, Reviews, Rules)
│   │   ├── schemas.py            # Pydantic validation schemas (OCRField, InspectionDetail, etc.)
│   │   ├── seed_rules.py         # 15 Member 2 statutory Legal Metrology rules
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ai_ocr.py         # Unified Quality Gate, Preprocessor, OCR, Proximity Matching
│   │       ├── rule_engine.py    # 15 Statutory rules evaluation engine
│   │       └── rule_version_resolver.py # Temporal rule version resolver
│   ├── tests/                    # 24 Automated Unit & Integration Tests
│   │   ├── __init__.py
│   │   ├── test_rule_engine.py
│   │   ├── test_database_apis.py
│   │   ├── test_review.py
│   │   └── test_integration_ai.py
│   └── uploads/                  # Evidence storage directory (auto-mounted at /uploads)
│
├── frontend/                     # React + Vite Legal Metrology Inspector Portal
│   ├── package.json              # NPM configuration
│   ├── vite.config.js            # Vite build setup with proxy to :8000
│   ├── tailwind.config.js        # Government of India theme styling
│   ├── dist/                     # Optimized production web bundle
│   └── src/
│       ├── api.js                # Unified REST API client (Auth, Dashboard, Scans, Reviews)
│       ├── App.jsx               # Navigation router and state provider
│       ├── main.jsx              # Application entrypoint
│       └── pages/
│           ├── Login.jsx         # Officer badge & PIN authentication
│           ├── InspectorHome.jsx # Live enforcement analytics & recent scans
│           ├── GuidedScan.jsx    # Evidence image upload & AI extraction
│           ├── ComplianceResult.jsx # Rule evaluation, bounding boxes & inspector override
│           └── Settings.jsx      # System diagnostics & rule registry
│
├── mobile/                       # Flutter Handheld Inspector Application
│   ├── pubspec.yaml              # Dependencies (http, flutter, etc.)
│   └── lib/
│       ├── main.dart             # App entrypoint
│       ├── api_service.dart      # Real multipart HTTP client to /inspection/quick-scan
│       ├── models.dart           # Data models (Declaration, InspectionStatus)
│       └── screens/
│           ├── scan_screen.dart  # Multi-camera package capture with real API call
│           └── result_screen.dart# Compliance breakdown & sign-off
│
├── samples/                      # Verified test assets
│   └── label.jpg                 # Standard packaged commodity test label
│
└── archive/                      # Historical prototypes safely quarantined
    ├── image_structure/
    └── label_analyzer/
```

---

## 4. Quickstart & Installation

### Prerequisites
- **Python 3.10+** (Tested on Python 3.11, 3.12, and 3.14)
- **Node.js 18+** & **npm**
- **Flutter SDK 3.x** (Optional, for mobile app development)
- **Git**

---

### Step 1: Backend Setup

1. Open PowerShell / Bash and navigate to the project directory:
   ```powershell
   cd "c:\finaal stage\backend"
   ```

2. Activate the virtual environment (or create one):
   ```powershell
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # (If creating new: python -m venv venv && .\venv\Scripts\Activate.ps1)
   ```

3. Install required packages (if not already installed):
   ```powershell
   pip install -r requirements.txt
   ```

4. Verify database creation and auto-seeding:
   ```powershell
   $env:PYTHONPATH = "."
   python -c "from app.database import create_tables; from app.seed_rules import seed_rules; create_tables(); seed_rules(); print('DB Ready!')"
   ```

---

### Step 2: Frontend Setup

1. In a second terminal window, navigate to `frontend/`:
   ```powershell
   cd "c:\finaal stage\frontend"
   ```

2. Ensure Node.js is in your PATH and install dependencies:
   ```powershell
   $env:PATH = "C:\Program Files\nodejs;$env:PATH"
   npm install
   ```

3. Verify production build:
   ```powershell
   npm run build
   ```

---

## 5. Starting the Services

### Start the Backend Server
From `c:\finaal stage\backend`:
```powershell
$env:PYTHONPATH = "."
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Backend will be available at: **`http://127.0.0.1:8000`**
* Interactive API Documentation (Swagger): **`http://127.0.0.1:8000/docs`**
* Alternative API Docs (ReDoc): **`http://127.0.0.1:8000/redoc`**

### Start the React Frontend Dashboard
From `c:\finaal stage\frontend`:
```powershell
$env:PATH = "C:\Program Files\nodejs;$env:PATH"
npm run dev
```
* Dashboard will be accessible at: **`http://localhost:5173`**

### (Optional) Run the Flutter Mobile App
From `c:\finaal stage\mobile`:
```powershell
flutter pub get
flutter run -d chrome  # or flutter run -d <device-id>
```

---

## 6. Pre-seeded Authorized Officer Credentials

The system includes pre-configured authorized Legal Metrology enforcement officers:

| Officer ID | Security PIN | Officer Name | Designation | Jurisdiction / Zone | Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`LMO-DEL-2024-884`** | **`8842`** | Rajesh Sharma | Legal Metrology Officer | North Delhi District - Circle 04 | Inspector |
| **`FSO-MH-001`** | **`1234`** | Suresh Patil | Legal Metrology Inspector | Mumbai Circle 01 | Inspector |
| **`DIR-CENTRAL-001`** | **`9999`** | Dr. Ananya Roy | Joint Director (Legal Metrology) | National Enforcement Command | Administrator |

*Note: On the login page, entering any of these Officer IDs and their matching PIN grants instant authenticated access with live JWT token issuance.*

---

## 7. Automated Test Suite

The test suite runs 24 comprehensive automated tests covering the deterministic rule engine, quality gate metrics, proximity matching, date separation, database CRUD, officer authentication, and live evidence upload.

To execute all tests:
```powershell
cd "c:\finaal stage\backend"
$env:PYTHONPATH = "."
$env:PYTHONIOENCODING = "utf-8"
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Verified Test Results:
```
test_analyze_then_review_flow (test_database_apis.DatabaseApiTests) ... ok
test_dashboard_reads_db (test_database_apis.DatabaseApiTests) ... ok
test_list_inspections_reads_db (test_database_apis.DatabaseApiTests) ... ok
test_missing_report_returns_404 (test_database_apis.DatabaseApiTests) ... ok
test_report_reads_db (test_database_apis.DatabaseApiTests) ... ok
test_all_supplied_rules_are_seeded (test_database_apis.SeededRulesTests) ... ok
test_rule_resolver_sees_seeded_rules (test_database_apis.SeededRulesTests) ... ok
test_auth_api_endpoint (test_integration_ai.AuthTests) ... ok
test_invalid_pin_fails (test_integration_ai.AuthTests) ... ok
test_valid_officer_login (test_integration_ai.AuthTests) ... ok
test_distant_number_rejected_as_mrp (test_integration_ai.ContextProximityTests) ... ok
test_mrp_within_distance_accepted (test_integration_ai.ContextProximityTests) ... ok
test_mfg_and_expiry_exclusion (test_integration_ai.DateSeparationTests) ... ok
test_quick_scan_with_image (test_integration_ai.EvidenceUploadApiTests) ... ok
test_blurry_flat_image_flagged (test_integration_ai.QualityGateTests) ... ok
test_sharp_image_passes (test_integration_ai.QualityGateTests) ... ok
test_review_is_saved_and_status_updated (test_review.ReviewPersistenceTests) ... ok
test_accepts_pass_fail_or_review_required (test_review.ReviewRequestTests) ... ok
test_rejects_unknown_decision (test_review.ReviewRequestTests) ... ok
test_high_confidence_present_required_field_passes (test_rule_engine.RuleEngineTests) ... ok
test_low_confidence_routes_to_human_review (test_rule_engine.RuleEngineTests) ... ok
test_missing_required_field_fails (test_rule_engine.RuleEngineTests) ... ok
test_no_rules_emits_per_field_review (test_rule_engine.RuleEngineTests) ... ok
test_unverified_rule_does_not_pass_or_fail (test_rule_engine.RuleEngineTests) ... ok

----------------------------------------------------------------------
Ran 24 tests in 5.391s

OK
```

---

## 8. Key API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health and engine version check | No |
| `POST` | `/auth/login` | Authenticate officer with `officer_id` and `pin` | No |
| `GET` | `/auth/me` | Retrieve authenticated officer profile | Yes (Bearer) |
| `GET` | `/dashboard` | Aggregate statistics and recent inspection records | Optional |
| `POST` | `/inspection/quick-scan` | Direct image upload, quality check, OCR & rule evaluation | Optional |
| `POST` | `/inspection` | Create inspection session record | Optional |
| `POST` | `/inspection/{id}/evidence` | Upload panel image (primary, MRP, manufacturer, etc.) | Optional |
| `POST` | `/inspection/{id}/review` | Submit inspector statutory override (PASS, FAIL, REVIEW_REQUIRED) | Optional |
| `GET` | `/inspection/{id}` | Full inspection details, declarations, violations, reviews | Optional |
| `GET` | `/rules/current` | Active Legal Metrology statutory rules | Optional |
| `GET` | `/reports/{id}` | Formal inspection notice and summary | Optional |

---

## 9. Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./niyamdrishti.db` | Database connection string. Use SQLite or PostgreSQL. |
| `AUTH_SECRET_KEY` | `niyamdrishti-sih-secret-2026-key` | Secret key for signing officer JWT tokens. |
| `EVIDENCE_STORAGE_PATH`| `./uploads/evidence` | Local directory for storing inspection evidence images. |
| `EASYOCR_DOWNLOAD` | `0` | Set `1` to auto-download EasyOCR deep-learning weights on first start. |
| `PORT` | `8000` | Backend listening port. |
| `HOST` | `0.0.0.0` | Backend bind host. |

---

## 10. Verification of Field Inspection Flow

Inspectors can verify the full cycle using the provided sample label:
1. Launch both backend (`:8000`) and frontend (`:5173`).
2. Log into the dashboard with `LMO-DEL-2024-884` and PIN `8842`.
3. Open **New Inspection / Quick Scan**.
4. Upload `samples/label.jpg`.
5. The system performs:
   - Quality validation (sharpness, lighting, resolution).
   - Unified OCR extraction with bounding box localization.
   - 15 Member 2 Legal Metrology rule checks.
   - Explainable violation report with legal section references.
6. The officer can review declarations, modify any low-confidence item, and submit a statutory sign-off (`PASS` / `FAIL`).
7. The decision is permanently logged in the audit database and updates the national enforcement dashboard immediately.
