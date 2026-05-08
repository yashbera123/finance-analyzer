# AI Personal Finance Behavior Analyzer

Full-stack finance analysis app for uploading transaction files, parsing and categorizing transactions, detecting behavioral patterns, and generating dashboard insights.

## Architecture

```text
.
├── client/                 # Next.js app router frontend
│   ├── public/             # Static frontend assets
│   └── src/
│       ├── app/            # App routes and layout
│       ├── components/     # UI, dashboard, chart, and upload components
│       ├── hooks/          # Client data/session hooks
│       └── lib/            # API client and utilities
├── server/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API router and endpoint modules
│   │   ├── core/           # Settings and database setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Parsing, analysis, categorization, reporting
│   │   └── utils/          # File helpers
│   ├── scripts/            # Parser fixtures and validation artifacts
│   ├── main.py             # FastAPI application entrypoint
│   └── requirements.txt
├── shared/                 # Reserved for shared contracts/types
├── scripts/                # Repository maintenance scripts
├── docs/                   # Project, cleanup, environment, deployment docs
├── data/manual-review/     # Preserved local data that needs human review
├── render.yaml             # Render backend blueprint
└── .github/workflows/      # CI checks
```

## Tech Stack

- Frontend: Next.js, React, Tailwind CSS, Framer Motion, Recharts
- Backend: FastAPI, SQLAlchemy, Pydantic, Uvicorn
- Data: SQLite for local development, PostgreSQL for production
- Deployment: Vercel for `client/`, Render for `server/`

## Local Development

Backend:

```powershell
cd server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```powershell
cd client
npm ci
copy .env.example .env.local
npm run dev
```

Open `http://localhost:3000`. The API runs at `http://localhost:8000`.

## Validation

```powershell
cd server
python -m compileall app main.py

cd ..\client
npm run lint
npm run build
```

## Deployment

See `docs/DEPLOYMENT.md` and `docs/ENVIRONMENT.md`.

## Important Data Note

Runtime uploads and SQLite databases are preserved locally but ignored by git. Move production data to managed storage and a managed PostgreSQL database before deploying.
