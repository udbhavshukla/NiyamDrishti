# Member 4 — Flutter / Mobile

## Responsibility
Field inspector smartphone app: capture label panels, upload to the backend,
display compliance results.

## Exact files / folders related to this work
| Path | Role |
|---|---|
| `mobile/pubspec.yaml` | Package manifest (`niyamdrishti_inspector`, Flutter SDK `>=3.0.0 <4.0.0`, `http`, `image_picker`) |
| `mobile/lib/main.dart` | App entry point, theme, home screen wiring |
| `mobile/lib/api_service.dart` | **Real** backend client: multipart image upload, `defaultApiUrl = http://10.0.2.2:8000` (Android emulator), `localhostApiUrl = http://localhost:8000` override |
| `mobile/lib/models.dart` | Client-side data models (`ComplianceResult`, `Declaration`, statuses) |
| `mobile/lib/screens/home_screen.dart` | Landing screen |
| `mobile/lib/screens/scan_screen.dart` | Capture + submit flow (imports `../api_service.dart`) |
| `mobile/lib/screens/result_screen.dart` | Result display (imports `../models.dart`) |

## Excluded on purpose
- `mobile/lib/mock_api.dart` from the original project was **not copied**: its own
  header says "TEMPORARY FILE - DELETE THIS ONCE MEMBER 3's REAL BACKEND API IS READY",
  and nothing imports it (`scan_screen.dart` already uses `api_service.dart`).

## Important APIs / components used
- `POST /inspection/quick-scan` (one-shot scan) and/or `POST /inspection/{id}/evidence`
  (per panel) with `Authorization: Bearer <token>` from `POST /auth/login`.

## Dependencies on other members
- **Member 3 (backend):** must be running and reachable; login credentials and response
  shapes come from `docs/API_GUIDE.md`.
- **Member 6:** device/emulator networking (`10.0.2.2` vs LAN IP) and release builds.

## What to understand before modifying code
1. Known gap (BUG-008): the current client uploads a single panel; multi-panel
   (front + MRP + manufacturer) flow is remaining work — backend already supports it.
2. Flutter SDK was not installed in the backend verification environment, so this app
   is uncompiled here; verify with `flutter analyze` / `flutter build apk` on your machine.
3. Keep response parsing aligned with `backend/app/schemas.py`, not with the old mock.
