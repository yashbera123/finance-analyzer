# Environment Variables

## Client

| Variable | Required | Description |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL, including `/api/v1`. Local default: `http://localhost:8000/api/v1`. |

Templates:

- `client/.env.example`
- `client/.env.production.example`

## Server

| Variable | Required | Description |
| --- | --- | --- |
| `APP_ENV` | Yes | `development` or `production`. |
| `SECRET_KEY` | Yes in production | Application secret. Replace the development placeholder before deploy. |
| `PORT` | Local optional | Local server port when running `python main.py`. Render injects `$PORT`. |
| `CORS_ORIGINS` | Yes | Comma-separated allowed frontend origins. |
| `DATABASE_URL` | Yes | Local SQLite or production PostgreSQL SQLAlchemy URL. |
| `OPENAI_API_KEY` | No | Reserved for OpenAI integration. |
| `GEMINI_API_KEY` | No | Reserved for Gemini integration. |
| `REDIS_URL` | No | Reserved for optional cache/session infrastructure. |

Templates:

- `server/.env.example`
- `server/.env.production.example`

## Production Notes

- Do not deploy with `SECRET_KEY=change-me-in-production`.
- Prefer PostgreSQL for production. SQLite files on ephemeral hosts can be lost.
- Set `CORS_ORIGINS` to the exact Vercel domain, not `*`.
- Keep real `.env`, `.env.local`, and provider keys out of git.
