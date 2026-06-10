# Pilot customer demo guide

Use this guide to demonstrate the AI Agent Platform to a first real pilot customer without adding new product features.

## What the pilot gets

- A dedicated company tenant with unique slug
- An owner login for the dashboard
- Website widget embed code
- Lead qualification, scoring, and email notifications
- A getting-started checklist inside the dashboard

## Option A: Self-serve onboarding (recommended for demos)

1. Open the landing page: http://localhost:3000
2. Click **Start your pilot**
3. Complete the two-step onboarding:
   - Company profile
   - Admin user
4. After sign-in, follow **Getting Started** in the dashboard:
   - Configure notification email in **Settings**
   - Copy the widget embed snippet
   - Mark the widget installed on the customer site
   - Send a test message in **Demo Chat**
5. Open **Leads** and confirm the captured lead appears

## Option B: Scripted setup (recommended for sales prep)

Create a ready-to-use pilot workspace from the backend container:

```bash
docker compose exec backend python -m app.scripts.setup_pilot_customer \
  --company-name "Acme Plumbing" \
  --company-email "hello@acme-plumbing.example" \
  --notification-email "leads@acme-plumbing.example" \
  --admin-email "owner@acme-plumbing.example" \
  --admin-password "choose-a-strong-password"
```

The script prints:

- Company slug for the widget
- Admin login credentials
- Widget embed snippet

Then sign in at http://localhost:3000/login and walk through **Getting Started**.

## Demo flow (15 minutes)

1. **Landing page** — explain widget + qualification + notifications
2. **Getting Started** — show checklist progress
3. **Settings** — notification email and widget snippet
4. **Demo Chat** — send a realistic customer message
5. **Leads** — show score, qualification status, and contactability
6. **Lead detail** — review captured fields and notification status

### Suggested test message

```text
Hi, I need an emergency plumber in Berlin tomorrow morning.
My kitchen sink is leaking badly. You can reach me at +49 170 1234567.
```

Follow up with name and email if the agent asks for them.

## Production checklist

Before a live pilot:

1. Set `OPENAI_API_KEY` in `.env`
2. Set `NOTIFICATION_PROVIDER=resend`
3. Set `RESEND_API_KEY` and `NOTIFICATION_FROM_EMAIL`
4. Set `FRONTEND_BASE_URL` to the public dashboard URL
5. Set `JWT_SECRET_KEY` to a long random value
6. Use a verified Resend sender domain

## Troubleshooting

| Issue | What to check |
| --- | --- |
| Demo chat fails | `OPENAI_API_KEY` configured and backend restarted |
| No email received | `NOTIFICATION_PROVIDER`, Resend keys, notification email in Settings |
| Widget does not load | `data-api-base` points to reachable API host |
| Empty leads table | Send a complete or contactable message above the score threshold |
| Cannot sign in | Use credentials from onboarding or setup script |

## URLs

- Landing page: http://localhost:3000
- Dashboard login: http://localhost:3000/login
- Getting started: http://localhost:3000/getting-started
- Widget prototype: http://localhost:8000/static/widget/embed.html
- API docs: http://localhost:8000/docs
