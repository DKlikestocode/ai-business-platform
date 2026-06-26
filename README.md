# AI Anfragen-Assistent

Multi-agent platform with a shared core, specialized agents, and a management dashboard.

## Architecture

```
AI Anfragen-Assistent
│
├── Core
│   ├── Auth
│   ├── Agent Engine
│   ├── Memory
│   ├── Tools
│   └── Workflows
│
├── Agents
│   ├── Lead Agent
│   ├── Email Agent
│   └── WhatsApp Agent
│
└── Dashboard
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/) v2+

## Quick start (development)

1. Clone the repository and move into the project directory:

```bash
cd ai-agent-platform
```

2. Create your local environment file:

```bash
cp .env.example .env
```

3. Start PostgreSQL, the FastAPI backend, and the dashboard:

```bash
docker compose up --build
```

4. Verify the services:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/ready
```

Expected responses:

- `/health` and `/api/v1/health` → `{"status":"ok"}`
- `/api/v1/health/ready` → `{"status":"ready","database":"connected"}`

5. Open the product and API docs:

- Landing page: http://localhost:3000
- Pilot onboarding: http://localhost:3000/onboarding
- Dashboard login: http://localhost:3000/login
- Getting started checklist: http://localhost:3000/getting-started
- Leads dashboard: http://localhost:3000/leads
- Lead Agent demo chat: http://localhost:3000/demo-chat
- Company settings: http://localhost:3000/settings
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Pilot customer demo

The dashboard now includes a public landing page, self-serve onboarding, and a post-login **Getting Started** checklist for pilot customers.

For a step-by-step walkthrough, see [docs/pilot-demo.md](docs/pilot-demo.md).

### Create a sample pilot customer from the CLI

```bash
docker compose exec backend python -m app.scripts.setup_pilot_customer \
  --company-name "Acme Plumbing" \
  --company-email "hello@acme-plumbing.example" \
  --notification-email "leads@acme-plumbing.example" \
  --admin-email "owner@acme-plumbing.example" \
  --admin-password "choose-a-strong-password"
```

This creates the company, owner user, optional notification email, and prints the widget embed snippet plus login details.

## Stopping services

```bash
docker compose down
```

To remove the database volume as well:

```bash
docker compose down -v
```

## Production

See [docs/deployment.md](docs/deployment.md) for the full runbook.

```bash
cp .env.production.example .env
# Set APP_ENV=production, JWT_SECRET_KEY, OPENAI_API_KEY, and other secrets

docker compose -f infrastructure/docker/docker-compose.prod.yml up --build -d
```

The production stack:

- Runs backend and frontend in production mode (not dev servers)
- Terminates TLS with Caddy (`app.example.com` → frontend, `api.example.com` → backend)
- Runs as a non-root user
- Uses multi-stage Docker builds
- Runs database migrations on startup
- Validates required secrets before startup
- Disables OpenAPI docs and self-service registration
- Includes health checks on `/api/v1/health/ready`

## Backend stack

| Component | Version / tool |
|-----------|----------------|
| Python | 3.14 |
| API | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Config | Pydantic Settings |

## Project layout

```
ai-agent-platform/
├── backend/
│   ├── app/                # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   ├── Dockerfile          # Development image
│   └── Dockerfile.prod     # Production image
├── frontend/
│   └── dashboard/          # Next.js leads dashboard
│       ├── app/
│       ├── components/
│       └── lib/
├── infrastructure/
│   ├── docker/             # Production compose file
│   ├── postgres/
│   └── n8n/
├── docs/
├── docker-compose.yml      # Development compose file
└── .env.example
```

## Local development without Docker

```bash
cd backend
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Start PostgreSQL separately, then:
cp ../.env.example ../.env
export $(grep -v '^#' ../.env | xargs)
export POSTGRES_HOST=localhost

alembic upgrade head
uvicorn app.main:app --reload
```

## Running tests

With Docker running:

```bash
docker compose exec backend pytest
```

Or locally inside `backend/` with dependencies installed:

```bash
pytest
```

## Database migrations

Create a new migration after adding models:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe change"
docker compose exec backend alembic upgrade head
```

## Frontend development

```bash
cd frontend/dashboard
cp .env.example .env.local
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` to your backend URL (default `http://localhost:8000`).

The dashboard proxies browser API calls through Next.js (`/api/v1/...` → backend), so you do not need cross-origin requests from the browser during local development.

With the full Docker stack running, the dashboard is available at http://localhost:3000/leads.

## Authentication

Sign in at http://localhost:3000/login. Dashboard routes require a JWT issued by:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secure-password"}'
```

Use the returned `access_token` as a Bearer token for protected API routes.

## Persistent conversations

Lead Agent chat history is stored in PostgreSQL per company. Each conversation is keyed by a client-provided `external_id` (for example `demo-chat-001`) and scoped to the authenticated user's `company_id`.

List persisted messages for a conversation:

```bash
curl http://localhost:8000/api/v1/conversations/demo-chat-001/messages \
  -H "Authorization: Bearer <access_token>"
```

Conversation records include `channel` (`web`, `whatsapp`, `email`, `api`) and `updated_at`. Messages store `role` (`user`, `assistant`, `system`, `tool`), `content`, optional `metadata` JSON, and `created_at`.

The shared Agent Runtime core still uses in-memory conversation storage for generic agent execution. Only the Lead Capture Agent flow uses database-backed conversations today.

## Embeddable website widget

The public widget endpoint lets customer websites send lead-capture chat messages without dashboard authentication. The backend resolves the tenant from `company_slug` and scopes all persistence internally.

```bash
curl -X POST http://localhost:8000/api/v1/public/widget/message \
  -H "Content-Type: application/json" \
  -d '{
    "company_slug": "demo-company",
    "conversation_id": "website-chat-001",
    "message": "Hi, I need a quote for roof repair in Berlin."
  }'
```

The response matches the authenticated demo chat shape: `reply`, `lead_complete`, `missing_fields`, `extracted_data`, and optional `lead_id`.

### Embed on a customer website

1. Ensure the company exists and note its `slug` (for example `demo-company`).
2. Add a container element to the page.
3. Load the widget script from your API host.

```html
<div
  id="ai-agent-widget"
  data-company-slug="your-company-slug"
  data-api-base="https://api.example.com"
  data-title="Chat with us"
></div>
<script src="https://api.example.com/static/widget/widget.js"></script>
```

Optional attributes:

- `data-company-slug` — tenant slug used to resolve the company
- `data-api-base` — API origin (defaults to the current page origin)
- `data-title` — widget header text
- `data-conversation-id` — stable conversation id for returning visitors

Prototype demo page:

```text
http://localhost:8000/static/widget/embed.html
```

Public widget requests allow cross-origin access from any website. Authenticated dashboard routes remain unchanged and still require JWT Bearer tokens.

## Lead notifications

The platform scores and qualifies leads during capture, then sends email notifications based on tenant settings.

### Lead qualification

Each lead stores:

- `contactable` — `true` when phone, email, or a WhatsApp channel contact path exists
- `contact_method` — `phone`, `email`, `channel`, or `unknown`
- `lead_score` — 0-100 based on captured context
- `qualification_status` — `incomplete`, `contactable`, or `qualified`

Scoring:

- +25 contact method
- +20 description
- +15 location
- +15 service_requested
- +10 urgency
- +10 name
- +5 preferred_callback_time

### Company notification settings

- `notification_email` — optional override recipient (falls back to company `email`)
- `notify_on_new_lead` — notify when `qualification_status=qualified`
- `notify_on_contactable_lead` — notify for contactable leads at or above the threshold
- `contactable_lead_notification_threshold` — defaults to `50`

Notification rules:

- Notify when a lead becomes `qualified`
- Or when `notify_on_contactable_lead=true`, the lead is contactable, and `lead_score` meets the threshold
- Never notify when `contactable=false`, except WhatsApp channel conversations
- `notification_sent_at` prevents duplicate notifications

The Lead Capture Agent prioritizes missing contact methods first, then asks for a stronger problem description, and confirms receipt once a lead is contactable with useful context.

Development uses the logging provider, which writes email content to application logs:

```bash
# In .env
NOTIFICATION_PROVIDER=logging
```

### Resend provider (production)

Set `NOTIFICATION_PROVIDER=resend` to deliver lead notifications through the [Resend](https://resend.com) HTTPS API:

```bash
NOTIFICATION_PROVIDER=resend
RESEND_API_KEY=re_xxxxxxxx
NOTIFICATION_FROM_EMAIL="Your Company <notifications@yourdomain.com>"
FRONTEND_BASE_URL=https://dashboard.example.com
```

Required when using Resend:

- `RESEND_API_KEY` — Resend API key
- `NOTIFICATION_FROM_EMAIL` — verified sender address in Resend

Optional:

- `FRONTEND_BASE_URL` — adds a `View in dashboard` link to notification emails

Each notification email includes the subject, recipient, lead summary, contact method, lead score, qualification status, and lead details. When `FRONTEND_BASE_URL` is set, the email also links to `/leads/{lead_id}` in the dashboard.

The SMTP provider interface remains a placeholder for future configuration.

## Company settings

Authenticated users can view and update their tenant settings from the dashboard **Settings** page (`/settings`) or via the API. All routes are scoped to the JWT user's `company_id`.

```bash
curl http://localhost:8000/api/v1/company/settings \
  -H "Authorization: Bearer <access_token>"
```

Editable fields:

- `name`, `email`, `phone`
- `notification_email`
- `notify_on_new_lead`
- `notify_on_contactable_lead`
- `contactable_lead_notification_threshold` (0–100)

Read-only fields:

- `slug` — used by the public website widget (`data-company-slug`)
- `created_at`

Update settings:

```bash
curl -X PATCH http://localhost:8000/api/v1/company/settings \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_email": "alerts@example.com",
    "contactable_lead_notification_threshold": 60
  }'
```

The Settings page also shows a copy-ready website widget embed snippet based on your company slug.

## Demo mode (development)

Seed five realistic German small-business demo leads (Dachdecker, Elektriker, Sanitär, Immobilienmakler, Fitnessstudio):

```bash
docker compose exec backend python -m app.scripts.seed_demo_data
```

Or use the **Create demo leads** button on the dashboard (visible when `NEXT_PUBLIC_APP_ENV=development`).

API endpoint (development only):

```bash
curl -X POST http://localhost:8000/api/v1/dev/seed-demo-data
```

Set `APP_ENV=development` for the backend and `NEXT_PUBLIC_APP_ENV=development` for the frontend. The dev endpoint returns `404` when `APP_ENV` is not `development`.
