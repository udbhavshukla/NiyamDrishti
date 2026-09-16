# Member 5 — Web Dashboard / Frontend

## Responsibility
React inspector portal: login, dashboard, guided scan, compliance results, review override.

## Exact files / folders related to this work
| Path | Role |
|---|---|
| `frontend/package.json` (+ `package-lock.json`) | React 18 + Vite 6 + react-router + Tailwind 3; reproducible install via lockfile |
| `frontend/vite.config.js` | Dev server on port 3000 |
| `frontend/src/api.js` | **Production API client**: login, dashboard, inspections, create, `scanImageEvidence` (quick-scan/evidence), `submitReviewOverride`, evidence `?token=` URL helper, offline/mock fallback |
| `frontend/src/pages/` | `Login.jsx`, `InspectorHome.jsx`, `GuidedScan.jsx`, `ComplianceResult.jsx` |
| `frontend/src/components/` | `Navbar`, `StatusBadge`, `MetricCard`, `EvidenceModal`, `NoticeModal`, `Footer` |
| `frontend/src/mockData.js` | Offline fallback data (imported by `api.js` + pages — required, not dead code) |
| `frontend/src/utils/soundEffects.js`, `src/App.jsx`, `src/main.jsx`, `src/index.css` | App wiring, styles, sounds |

## Important APIs / components used
- Base URL: `VITE_API_BASE_URL` env or `http://localhost:8000`.
- Token stored as `niyam_token` in localStorage; evidence `<img>` URLs append `?token=`.
- Review flow posts to `/inspection/{id}/review` (see `docs/API_GUIDE.md`).

## Dependencies on other members
- **Member 3 (backend):** API shapes and auth; when backend is unreachable the app runs
  in offline/mock mode (by design).
- **Member 6:** Node 18+, `npm install`, production build + hosting.

## What to understand before modifying code
1. Known gaps (see `PROJECT_STATUS.md`): hardcoded demo PINs in the offline fallback
   (BUG-006), hardcoded officer profile on InspectorHome (BUG-004), GuidedScan timer
   race (BUG-005). Fix against the real backend, not the mocks.
2. Node.js was not installed in the backend verification environment; the React build
   was not re-verified here. Run `npm install && npm run build` on your machine.
3. Do not remove `mockData.js` — it is the offline fallback, imported in 9 files.
