# Production Deployment

This guide covers deploying the AI Agent Platform with Docker Compose for a pilot or small production environment.

## Prerequisites

- Docker and Docker Compose
- A `.env` file based on `.env.production.example`
- TLS termination via a reverse proxy (Caddy, nginx, Traefik, or a cloud load balancer)
- A Resend API key for lead notification emails

## Required environment variables

| Variable | Description |
|----------|-------------|
| `APP_ENV` | Must be `production` |
| `JWT_SECRET_KEY` | Unique secret, at least 32 characters |
| `OPENAI_API_KEY` | OpenAI API key for the Lead Capture Agent |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Database credentials |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `NEXT_PUBLIC_API_URL` | Public API URL used by the browser |
| `FRONTEND_BASE_URL` | Public dashboard URL for email links |
| `NOTIFICATION_PROVIDER` | Set to `resend` in production |
| `RESEND_API_KEY` | Resend API key |
| `NOTIFICATION_FROM_EMAIL` | Verified sender address in Resend |

The backend refuses to start in production if `JWT_SECRET_KEY` is still the default value or if `OPENAI_API_KEY` is missing.

## Deploy

```bash
cp .env.production.example .env
# Edit .env with production values

docker compose -f infrastructure/docker/docker-compose.prod.yml up --build -d
```

The production stack runs:

- PostgreSQL with a persistent volume
- Backend (migrations on startup, single Uvicorn worker, non-root user)
- Frontend (`next build` + `next start`)

## Health checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness probe |
| `GET /api/v1/health` | API liveness |
| `GET /api/v1/health/ready` | Readiness (includes database connectivity) |

Use `/api/v1/health/ready` for orchestrator readiness checks.

## Security defaults in production

- OpenAPI docs (`/docs`, `/redoc`) are disabled
- Self-service company/user registration is disabled (`POST /companies`, `POST /users`)
- Login and public widget endpoints are rate-limited
- Security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) are added

Provision new tenants with the pilot setup script or an internal admin process:

```bash
docker compose -f infrastructure/docker/docker-compose.prod.yml exec backend \
  python -m app.scripts.setup_pilot_customer
```

## TLS

The Compose file does not terminate TLS. Place a reverse proxy in front of the frontend and backend ports, or use a managed platform that provides HTTPS.

## Database backups

Back up the Postgres volume regularly:

```bash
docker compose -f infrastructure/docker/docker-compose.prod.yml exec postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
```

## Rollback

1. Stop the stack: `docker compose -f infrastructure/docker/docker-compose.prod.yml down`
2. Restore the database from backup if needed
3. Deploy the previous image tag or git revision
4. Start the stack again

## CI

GitHub Actions runs backend tests (with Postgres), frontend tests, and a production frontend build on every push and pull request.
