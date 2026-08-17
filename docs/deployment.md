# Production Deployment

This guide covers deploying AI Anfragen-Assistent with Docker Compose for a pilot or small production environment.

## Prerequisites

- Docker and Docker Compose
- A `.env` file based on `.env.production.example`
- Two DNS A records pointing at your server (see [DNS setup](#dns-setup))
- A Resend API key for lead notification emails

## Required environment variables

| Variable | Description |
|----------|-------------|
| `APP_ENV` | Must be `production` |
| `APP_DOMAIN` | Public dashboard hostname (e.g. `app.example.com`) |
| `API_DOMAIN` | Public API hostname (e.g. `api.example.com`) |
| `SITE_DOMAIN` | Root marketing site with widget embed (e.g. `example.com, www.example.com`) |
| `PILOT_COMPANY_SLUG` | Company slug for the public business website (`SITE_DOMAIN`) |
| `SITE_COMPANY_SLUG` | Alias for `PILOT_COMPANY_SLUG` (frontend runtime) |
| `ACME_EMAIL` | Email for Let's Encrypt certificate notifications |
| `JWT_SECRET_KEY` | Unique secret, at least 32 characters |
| `OPENAI_API_KEY` | OpenAI API key for the Lead Capture Agent |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Database credentials |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins (`https://app.example.com`) |
| `NEXT_PUBLIC_API_URL` | Public API URL (`https://api.example.com`) |
| `PUBLIC_API_BASE_URL` | Public API URL used in customer widget embed code (`https://api.example.com`) |
| `FRONTEND_BASE_URL` | Public dashboard URL for email links (`https://app.example.com`) |
| `WIDGET_STALE_AFTER_HOURS` | Hours without widget heartbeat before status shows as stale (default `168`) |
| `NOTIFICATION_PROVIDER` | Set to `resend` in production |
| `RESEND_API_KEY` | Resend API key |
| `NOTIFICATION_FROM_EMAIL` | Verified sender address in Resend |
| `INTAKE_EMAIL_ENABLED` | Set to `true` after the inbound domain and webhook are ready |
| `RESEND_WEBHOOK_SECRET` | Signing secret of the Resend `email.received` webhook |
| `RESEND_INBOUND_DOMAIN` | Dedicated receiving subdomain, e.g. `inbox.example.com` |

The backend refuses to start in production if `JWT_SECRET_KEY` is still the default value or if `OPENAI_API_KEY` is missing. When inbound email is enabled, it also requires the webhook secret and a valid inbound domain.

## DNS setup

Point these domains at the public IP of the server running Docker Compose.

| Type | Name | Value |
|------|------|-------|
| A | `app.example.com` | Your server public IP |
| A | `api.example.com` | Your server public IP |
| A | `@` (apex) | Your server public IP |
| A | `www` | Your server public IP |

Wait for DNS to propagate before starting the stack. Caddy requests Let's Encrypt certificates during startup and requires both hostnames to resolve to this server.

Verify DNS:

```bash
dig +short app.example.com
dig +short api.example.com
```

Configure the dedicated `RESEND_INBOUND_DOMAIN` separately in Resend Receiving using the DNS records shown there. Subscribe a webhook to the `email.received` event and point it to:

```text
https://api.example.com/api/v1/webhooks/resend
```

Do not point the inbound email subdomain at Caddy unless Resend explicitly asks for such a record.

## Reverse proxy and HTTPS

Production uses [Caddy](https://caddyserver.com/) as the reverse proxy with automatic HTTPS via Let's Encrypt.

| Public URL | Routes to | Purpose |
|------------|-----------|---------|
| `https://app.example.com` | `frontend:3000` | Dashboard UI |
| `https://api.example.com` | `backend:8000` | REST API and static assets |
| `https://example.com` | `Caddy file_server` → `infrastructure/docker/www` | Pilot marketing site with widget |

The Caddy configuration lives in `infrastructure/docker/Caddyfile.template`. Domain values are injected from `.env` at runtime using `{$APP_DOMAIN}`, `{$API_DOMAIN}`, `{$SITE_DOMAIN}`, and `{$ACME_EMAIL}`.

Backend and frontend are not published directly. Only Caddy exposes ports `80` and `443`.

### Widget script on the API domain

Customer websites embed the widget from the API domain:

```html
<script src="https://api.example.com/static/widget/widget.js"></script>
<script>
  window.AIAgentWidget && window.AIAgentWidget.init({
    companySlug: "your-company-slug",
    apiBaseUrl: "https://api.example.com",
  });
</script>
```

Caddy forwards all `api.example.com` traffic to the backend, including `/static/widget/widget.js` and `/api/v1/public/*` widget message endpoints.

### Pilot marketing site (`SITE_DOMAIN`)

The root domain is served by the **Next.js business site** at `/site`, routed by hostname via middleware. Caddy proxies `SITE_DOMAIN` to the frontend container (same stack as the dashboard).

Configure in `.env`:

```env
SITE_DOMAIN=example.com, www.example.com
PILOT_COMPANY_SLUG=your-company-slug
```

Local preview without custom DNS: `http://localhost:3000/site`

**Legacy fallback:** `infrastructure/docker/scripts/generate-www.sh` can still emit static HTML from the backend script if needed.

## Deploy

```bash
cp .env.production.example .env
# Edit .env with production values, including APP_DOMAIN, API_DOMAIN, and ACME_EMAIL

docker compose -f infrastructure/docker/docker-compose.prod.yml up --build -d
```

The production stack runs:

- PostgreSQL with a persistent volume
- Backend (migrations on startup, single Uvicorn worker, non-root user)
- Intake worker for durable email/PDF processing and retries
- Frontend (`next build` + `next start`)
- Caddy (TLS termination and reverse proxy)

## Health checks

| Endpoint | Purpose |
|----------|---------|
| `GET https://api.example.com/health` | Liveness probe |
| `GET https://api.example.com/api/v1/health` | API liveness |
| `GET https://api.example.com/api/v1/health/ready` | Readiness (includes database connectivity) |

Use `/api/v1/health/ready` for orchestrator readiness checks.

## Security defaults in production

- Automatic HTTPS with HTTP → HTTPS redirects (Caddy)
- OpenAPI docs (`/docs`, `/redoc`) are disabled
- Self-service company/user registration is disabled (`POST /companies`, `POST /users`)
- Login and public widget endpoints are rate-limited
- Security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) are added

Provision new tenants with the pilot setup script or an internal admin process:

```bash
docker compose -f infrastructure/docker/docker-compose.prod.yml exec backend \
  python -m app.scripts.setup_pilot_customer
```

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

Certificate data is stored in the `caddy_data` Docker volume and is preserved across restarts.

## CI

GitHub Actions runs backend tests (with Postgres), frontend tests, and a production frontend build on every push and pull request.
