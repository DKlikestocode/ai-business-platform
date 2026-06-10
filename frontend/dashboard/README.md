# Leads Dashboard

Next.js dashboard for reviewing and updating captured leads.

## Environment

Copy the example env file:

```bash
cp .env.example .env.local
```

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Public backend URL reference | `http://localhost:8000` |
| `API_INTERNAL_URL` | Server-side proxy target in Docker | `http://backend:8000` |
| `NEXT_PUBLIC_APP_ENV` | Shows dev-only UI controls | `development` |

Browser API calls use **same-origin** paths like `/api/v1/...`. Next.js rewrites those requests to the backend, which avoids browser CORS issues during local development.

When running locally without Docker, set:

```bash
API_INTERNAL_URL=http://localhost:8000
```

## Local development

```bash
npm install
npm run dev
```

Open http://localhost:3000

## Docker

From the project root:

```bash
docker compose up --build frontend
```

Or start the full stack:

```bash
docker compose up --build
```

Dashboard: http://localhost:3000  
Leads list: http://localhost:3000/leads

In development, use **Create demo leads** to populate five German demo scenarios via `POST /api/v1/dev/seed-demo-data`.

## Features

- Lead list with pagination
- Status filter
- Inline status updates via PATCH
- Lead detail page at `/leads/{id}`
- Lead Agent demo chat at `/demo-chat`

## Demo chat

Open http://localhost:3000/demo-chat to test the Lead Capture Agent in a simple chat UI.

- Uses a fixed demo conversation ID (`demo-chat-001`) by default
- Click **New conversation** to start fresh with a new ID
- Sends messages to `POST /api/v1/agents/lead/message`
- When the lead is complete, a success message links to the created lead detail page

Requires a valid `OPENAI_API_KEY` in the backend `.env` for live agent responses.
