# Deployment

## Vercel Frontend

Use `client/` as the Vercel project root directory.

Settings:

```text
Framework Preset: Next.js
Root Directory: client
Install Command: npm ci
Build Command: npm run build
Output Directory: .next
```

Environment variables:

```text
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api/v1
```

CLI deployment:

```powershell
cd client
npm ci
npm run build
npx vercel deploy
npx vercel deploy --prod
```

## Render Backend

Use the root `render.yaml` blueprint or create a Render Web Service manually.

Blueprint values:

```text
Root Directory: server
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Health Check Path: /health
```

Required production environment variables:

```text
APP_ENV=production
SECRET_KEY=replace-with-a-long-random-secret
CORS_ORIGINS=https://your-vercel-project.vercel.app
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/finance_db
```

Manual local production smoke test:

```powershell
cd server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:APP_ENV='production'
$env:CORS_ORIGINS='http://localhost:3000'
$env:DATABASE_URL='sqlite+aiosqlite:///./finance_analyzer.db'
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Production Data

The local `server/uploads/` directory and SQLite database are preserved for manual review. For production, use managed object storage for uploaded files and a managed PostgreSQL database for durable sessions and analysis data.
