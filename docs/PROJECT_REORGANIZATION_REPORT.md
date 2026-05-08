# Project Reorganization Report

Generated: 2026-05-08

## Scope

Repository scanned from:

```text
C:\Users\byash\Downloads\finance-analyzer-v3
```

The real application repository was found nested at:

```text
C:\Users\byash\Downloads\finance-analyzer-v3\finance-analyzer-v2
```

The outer directory also contained an archive metadata folder (`__MACOSX`) and a root-level SQLite database (`finance_analyzer.db`). The nested application repository has its own `.git` directory and active uncommitted source changes, so all source files are being preserved.

Post-restructure note: this report records the pre-cleanup inventory. During restructuring, `frontend/` was promoted to `client/`, `backend/` was promoted to `server/`, and the nested repository was promoted to the current working-folder root.

## Technology Detection

| Area | Detected | Evidence |
| --- | --- | --- |
| React | Yes | `frontend/package.json` includes `react` and `react-dom` |
| Next.js | Yes | `frontend/package.json`, `next.config.mjs`, `src/app/*` |
| Vite | No | No `vite.config.*` or Vite dependency detected |
| Tailwind | Yes | `tailwindcss`, `@tailwindcss/postcss`, `@import "tailwindcss"` |
| TypeScript | Partial/tooling only | JavaScript app, TypeScript package present as dependency of tooling; no app `tsconfig.json` |
| Node.js | Yes | Next.js frontend |
| Express | No | No Express dependency or server code detected |
| Python backend | Yes | `backend/main.py`, `requirements.txt` |
| FastAPI | Yes | `fastapi` dependency and `FastAPI(...)` app |
| Flask | No | No Flask dependency or app detected |
| SQLite | Yes | default `sqlite+aiosqlite:///./finance_analyzer.db`, `.db` files present |
| PostgreSQL | Supported | SQLAlchemy asyncpg dependencies and Postgres model types |
| MongoDB | No | No MongoDB dependency or config detected |
| Firebase | No | No Firebase dependency or config detected |
| Docker | No | No Dockerfile or compose file detected |
| Deployment | Yes | `frontend/vercel.json`, `backend/render.yaml` |

## Package Managers And Build Systems

- Frontend package manager: npm (`package-lock.json` present).
- Frontend build: Next.js (`npm run build`, output `.next`).
- Backend package manager: pip (`requirements.txt`).
- Backend runtime: Uvicorn/FastAPI (`uvicorn main:app --host 0.0.0.0 --port $PORT`).
- No root monorepo package manager was present before restructuring.

## Critical Source Inventory

### Frontend

- App routes:
  - `frontend/src/app/page.js`
  - `frontend/src/app/dashboard/page.js`
  - `frontend/src/app/insights/page.js`
  - `frontend/src/app/transactions/page.js`
  - `frontend/src/app/layout.js`
  - `frontend/src/app/globals.css`
- Components:
  - `frontend/src/components/SessionProvider.jsx`
  - `frontend/src/components/charts/*`
  - `frontend/src/components/dashboard/*`
  - `frontend/src/components/ui/*`
  - `frontend/src/components/upload/*`
- Hooks:
  - `frontend/src/hooks/useDashboard.js`
  - `frontend/src/hooks/useInsights.js`
  - `frontend/src/hooks/useTransactions.js`
  - `frontend/src/hooks/useUpload.js`
- Utilities/API:
  - `frontend/src/lib/api.js`
  - `frontend/src/lib/session.js`
  - `frontend/src/lib/utils.js`
- Assets:
  - `frontend/public/*.svg`
  - `frontend/src/app/favicon.ico`

### Backend

- Entrypoint:
  - `backend/main.py`
- API router:
  - `backend/app/api/router.py`
- Endpoint modules:
  - `analyze.py`
  - `categorize.py`
  - `dashboard.py`
  - `insights.py`
  - `parse.py`
  - `profile.py`
  - `report.py`
  - `session.py`
  - `transactions.py`
  - `upload.py`
- Core/config/database:
  - `backend/app/core/config.py`
  - `backend/app/core/database.py`
- Models:
  - `analysis.py`
  - `analysis_session.py`
  - `transaction.py`
  - `upload.py`
  - `user.py`
- Schemas:
  - `analysis.py`
  - `category.py`
  - `dashboard.py`
  - `profile.py`
  - `session.py`
  - `transaction.py`
  - `upload.py`
- Services:
  - `analysis_session_service.py`
  - `analyzer.py`
  - `categorizer.py`
  - `dashboard_builder.py`
  - `parser.py`
  - `profiler.py`
  - `report.py`
  - `store.py`
- Utilities:
  - `backend/app/utils/file_helpers.py`
- Scripts/test data:
  - `backend/scripts/parser_test_report.json`
  - `backend/scripts/test_data/*`

## API Surface

Mounted base path: `/api/v1`

Detected routes:

- `GET /`
- `GET /health`
- `GET /api/v1/ping`
- `POST /api/v1/upload/`
- `POST /api/v1/parse/{file_id}`
- `POST /api/v1/parse/{file_id}/correct`
- `POST /api/v1/categorize/{file_id}`
- `POST /api/v1/analyze/{file_id}`
- `POST /api/v1/profile/{file_id}`
- `GET /api/v1/dashboard/{file_id}`
- `GET /api/v1/insights/{file_id}`
- `GET /api/v1/transactions/{file_id}`
- `GET /api/v1/report/{file_id}`
- `GET /api/v1/session/{session_id}`

## Configuration Inventory

- Repository:
  - `.gitignore`
  - `.git`
  - `README.md`
- Frontend:
  - `package.json`
  - `package-lock.json`
  - `next.config.mjs`
  - `eslint.config.mjs`
  - `postcss.config.mjs`
  - `jsconfig.json`
  - `.env.example`
  - `.env.local`
  - `vercel.json`
- Backend:
  - `requirements.txt`
  - `.env.example`
  - `.gitignore`
  - `render.yaml`

## Database And Data Inventory

- `backend/finance_analyzer.db`:
  - Runtime SQLite database used by local default `DATABASE_URL`.
  - Preserved because it may contain user/session data.
- Outer `finance_analyzer.db`:
  - Database file outside the nested app.
  - Preserved for manual review because it may contain historical data.
- `backend/uploads/*`:
  - Runtime uploaded CSV/XLSX/PDF files.
  - Preserved because uploads may be user data and are not always reproducible.
- Migrations:
  - No migration folder detected.
  - `alembic` is listed in requirements, but no Alembic config/env was found.

## Generated Or Reproducible Artifacts

The following are safe to regenerate and eligible for cleanup:

- `__MACOSX/`
  - Archive metadata from macOS extraction.
  - Not required by runtime, build, or deployment.
- `frontend/node_modules/`
  - Reproducible from `frontend/package-lock.json` via `npm ci`.
- `frontend/.next/`
  - Reproducible Next.js build/dev output from `npm run build` or `npm run dev`.
- `backend/.venv/`
  - Reproducible Python virtual environment from `backend/requirements.txt`.
  - Also appears platform-specific from the archive and should not be committed.
- `__pycache__/` and `*.pyc`
  - Reproducible Python bytecode caches.

## Preserved For Manual Review

These are not being deleted automatically:

- `backend/uploads/*`
  - Runtime uploads; may contain user files.
- `backend/finance_analyzer.db`
  - Runtime SQLite database; may contain local session data.
- outer `finance_analyzer.db`
  - Duplicate-looking database outside the app root, but may contain data.
- `backend/scripts/test_data/*`
  - Parser fixtures and test files; useful for validation and not generated.
- `.env.example` files and `.env.local`
  - Environment configuration/template files.

## Potential Issues Detected

- Existing source worktree is dirty; all user changes must be preserved.
- The project is nested one level deeper than the current working folder.
- Vercel and Render configs are split under `frontend/` and `backend/`; a root deployment guide/config would be clearer after restructuring.
- Backend environment template uses `GOOGLE_API_KEY`, while application settings define `GEMINI_API_KEY`.
- `SECRET_KEY` and `REDIS_URL` exist in settings but are missing from the backend env template.
- No Alembic migration environment exists, despite `alembic` being listed.
- Runtime uploads and SQLite DB are inside the backend app directory; deployment should use external storage or a managed database for production.
- Real `.env.local` is present locally; it currently contains no secret value, but real env files should remain ignored.

## Cleanup Decision

Destructive cleanup is limited to confirmed generated/reproducible artifacts only. Runtime data, databases, source, configs, scripts, and deployment files are preserved.
