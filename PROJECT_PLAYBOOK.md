# Project Playbook

**How this product is built.** Project-specific handbook for engineers, product, and operators.

| Document | Scope |
|----------|--------|
| `PRODUCT_CONSTITUTION.md` | Timeless product principles — what we will and will not become |
| `AGENTS.md` | Engineering standards, workflow, and quality bars |
| **This file** | Current product shape, modules, risks, and direction |

---

# Product Overview

AI Anfragen-Assistent is an AI employee for small service businesses: it captures website inquiries through a conversational interface, extracts who needs what and how urgently, notifies the business when an inquiry is worth acting on, and presents a clear inbox so the owner can call or email back. The product is German-first, built for Handwerk and local Dienstleister who think in phone calls and Posteingang — not CRM pipelines or SaaS administration.

---

# Vision

Every service business worldwide has a reliable first responder on its website — one that never sleeps, never forgets to ask for a phone number, and never hands the owner a useless chat log. We become the default layer between a business's website and its phone: trusted, lawful, invisible when working, and indispensable after the first saved job.

---

# Core User Journey

```
Landing
  → Signup (company + owner)
  → Login
  → Onboarding / Getting Started
  → Widget embedded on customer's website
  → End customer has AI conversation on that website
  → Inquiry captured and qualified
  → Dashboard inbox
  → Owner contacts end customer (phone / email)
```

**North-star metric:** Time from signup to the first **real** inquiry from the customer's live website — contactable, complete, and acted on.

**Critical distinction:** Test-Chat in the dashboard exercises the same AI but is not proof the website loop works. Product and onboarding must never blur the two.

---

# Primary Users

### 1. Business owner (primary)

- Runs a service company with 1–20 people: Sanitär, Dach, Elektro, Immobilien, Fitness, and similar.
- Low technical literacy. Uses email, phone, maybe WordPress. Does not know what an API or slug is.
- Checks inquiries between jobs, often on mobile.
- Success = understands each inquiry in seconds and knows whom to call.

### 2. Office manager / back office (secondary)

- Same mental model as the owner. May handle inbox and status updates daily.
- Needs reliability and plain language more than configuration depth.

### 3. Pilot operator / internal sales (internal)

- Provisions tenants, runs demos, supports first embed.
- Uses CLI setup in production today; self-serve signup in development only.
- Needs a repeatable 15-minute demo that ends in a believable inbox.

### 4. End customer (indirect)

- Visitor on the business's website with a problem (leak, quote, emergency).
- Wants fast answers and a callback — not a form, not jargon, not a dead end.

---

# Product Modules

## Marketing

| | |
|---|---|
| **Purpose** | Acquire pilots. Communicate value (capture, qualify, notify), build trust (DSGVO, Impressum, professional tone), drive signup. |
| **Owner** | Product + Growth |
| **Dependencies** | Onboarding entry, Auth entry, legal pages |
| **Future evolution** | Vertical-specific landing (Sanitär vs Dach), case studies from real pilots, live proof of widget — not illustrative mockups only |

## Authentication

| | |
|---|---|
| **Purpose** | Secure dashboard access per tenant. Email/password login, session cookie, route protection. |
| **Owner** | Platform / Security |
| **Dependencies** | Users and companies in database, JWT issuance, frontend session bridge |
| **Future evolution** | Password reset, optional SSO for agencies — not before core loop is proven. No role complexity until team features exist. |

## Onboarding

| | |
|---|---|
| **Purpose** | Create tenant and owner; guide first-time setup via Getting Started checklist (notification email, widget snippet, install acknowledgment, test chat). |
| **Owner** | Activation |
| **Dependencies** | Auth, Settings, Widget embed, Test-Chat |
| **Future evolution** | Server-verified progress; honest widget-live detection; production self-serve when provisioning is automated. Checklist should reward real website inquiry, not demo alone. |

## Dashboard

| | |
|---|---|
| **Purpose** | Posteingang for inquiries: list, filter, sort, status, detail view, contact actions. Stable shell, fast navigation, empty states that teach. |
| **Owner** | Product + Frontend |
| **Dependencies** | Auth, Inquiry Pipeline API, i18n |
| **Future evolution** | Cards-first inbox at low volume; cached navigation; optional analytics (response time, conversion) — never a full CRM. |

## AI Chat (Test-Chat)

| | |
|---|---|
| **Purpose** | Authenticated sandbox to exercise Lead Capture Agent before or alongside live widget. Onboarding step and sales demo tool. |
| **Owner** | AI + Product |
| **Dependencies** | Auth, Lead Capture Agent, OpenAI |
| **Future evolution** | Clearly labeled as test channel; optional side-by-side with live widget health. Same agent quality as public widget — diverging behavior is a defect. |

## Widget

| | |
|---|---|
| **Purpose** | Embeddable chat on customer websites. Public API keyed by company slug. The product's front door on the internet. |
| **Owner** | Platform + Frontend (embed) + AI |
| **Dependencies** | Inquiry Pipeline, company slug, API host, CORS policy |
| **Future evolution** | Widget health in dashboard, appearance options within brand guardrails, locale-aware visitor copy, one-click install paths for WordPress and common site builders. |

## Inquiry Pipeline

| | |
|---|---|
| **Purpose** | End-to-end path: message → conversation → extraction → qualification/scoring → lead record → notification trigger. German Sie-form, trades-aware prompts. |
| **Owner** | AI + Backend |
| **Dependencies** | OpenAI, PostgreSQL, Notifications, Company settings |
| **Future evolution** | Channel parity (web today; WhatsApp/email stubs in model layer). Evaluation harness on real German scenarios. Structured handoff quality over chat length. |

## Settings

| | |
|---|---|
| **Purpose** | Company profile, notification recipient, alert rules, widget embed snippet. Bridge between dashboard and live website. |
| **Owner** | Product |
| **Dependencies** | Auth, Company service |
| **Future evolution** | Hide internal thresholds behind plain-language controls. Widget verification status. Agency-managed settings for multi-site customers later. |

## Notifications

| | |
|---|---|
| **Purpose** | Alert owner when an inquiry crosses qualification threshold. Email via Resend in production; logging in development. |
| **Owner** | Platform |
| **Dependencies** | Inquiry Pipeline, company notification settings, verified sender domain |
| **Future evolution** | SMS for urgent trades, digest mode, in-app notification center. SMTP as fallback only if needed. |

## Admin

| | |
|---|---|
| **Purpose** | Tenant provisioning and operator tooling. Today: CLI (`setup_pilot_customer`), dev seed endpoints — no operator UI. User roles exist in data model; no team management surface. |
| **Owner** | Platform |
| **Dependencies** | Companies, users repositories |
| **Future evolution** | Internal admin for tenant lifecycle, billing hooks, support impersonation with audit — only when pilot count justifies it. Not a customer-facing admin panel. |

---

# Architecture Map

```
┌──────────────────────────────────────────────────────────────────┐
│  End customer browser (business website)                         │
│       embed script → public widget API                           │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│  API layer (FastAPI)                                             │
│    Auth · Public widget · Leads · Settings · Lead agent          │
│    Tenant isolation by company_id / company_slug                 │
└────────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Lead Capture  │   │ PostgreSQL    │   │ Notifications │
│ Agent + LLM   │   │ leads, convs, │   │ Resend / log  │
│               │   │ messages, cos │   │               │
└───────────────┘   └───────────────┘   └───────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Business owner browser (dashboard)                              │
│       Next.js · next-intl (de/en) · same-origin API proxy        │
│       Marketing · Onboarding · Inbox · Settings · Test-Chat      │
└──────────────────────────────────────────────────────────────────┘

Production: Caddy TLS → app.* (frontend) + api.* (backend + static widget)
Development: Docker Compose — Postgres, backend, frontend bind-mount
```

**Layer discipline:** Routes thin → services own business rules → repositories own queries → components own presentation. Shared agent runtime exists; only Lead Capture is production-complete on persistent storage.

**Related docs:** `docs/architecture.md` (aspirational multi-agent view), `docs/deployment.md` (production runbook), `AGENTS.md` (implementation rules).

---

# Current Technical Debt

Ranked by impact on shipping and operating the core loop.

1. **Documentation drift** — README and `docs/architecture.md` describe Email/WhatsApp agents and n8n workflows that are not built. Misleads new engineers and partners.
2. **Onboarding honesty gap** — Progress stored in browser localStorage; widget install is manual checkbox, not verified on live site.
3. **Test-Chat vs website ambiguity** — Same agent, different channels; product can imply success without a real website inquiry.
4. **Production provisioning** — Self-serve signup disabled in production; every tenant requires CLI or internal process.
5. **Brand** — Product name is **AI Anfragen-Assistent** (DE) / **AI Inquiry Assistant** (EN) across marketing and dashboard.
6. **Widget visitor experience** — Hardcoded German in embed script; no locale alignment with business or visitor.
7. **Dual conversation storage** — Lead agent persists to PostgreSQL; generic agent runtime still in-memory. Confusing mental model for extending agents.
8. **Notification fallback** — SMTP provider is a stub; production depends entirely on Resend configuration discipline.
9. **Empty planning artifacts** — `docs/ROADMAP.md` empty; `infrastructure/n8n/` and `infrastructure/postgres/` are placeholders.
10. **Dashboard data freshness** — Company settings cached; leads still refetch on navigation — perceived flicker undermines speed principles.

---

# Product Risks

1. **False activation** — Owner completes onboarding and test chat but never embeds widget; churns believing product failed.
2. **OpenAI single point of failure** — Production refuses to start without key; outages or cost spikes hit every conversation.
3. **Inquiry quality variance** — Agent may miss phone number, urgency, or location on edge-case German phrasing; owner loses trust after one bad handoff.
4. **Notification failure silent to user** — Misconfigured Resend or wrong notification email; inquiries exist in dashboard but owner never knows.
5. **Public widget abuse** — Open CORS on public API; slug guessing and spam require monitoring and rate limits as volume grows.
6. **DSGVO and transparency** — AI on customer websites without clear disclosure where required; legal exposure for pilots.
7. **Scope creep into CRM** — Pressure to add pipelines and automation before inbox excellence; dilutes positioning.
8. **Pilot scale without admin tooling** — Manual tenant setup does not scale past a handful of customers.
9. **Competitor "good enough" widget** — Intercom/Drift-style tools with established embed paths; we must win on inquiry quality and Handwerk fit, not feature count.
10. **English parity lag** — EN copy exists but German pilots drive decisions; EN-only bugs hide until expansion.

---

# Current Bottlenecks

1. **No in-product widget verification** — Cannot confirm embed is live on customer's domain.
2. **Manual production onboarding** — CLI/script required per tenant.
3. **First real website inquiry** — Primary success metric; most pilots likely stall before this event.
4. **Demo-dependent sales motion** — 15-minute scripted flow; not self-serve at scale.
5. **Single agent depth** — All value flows through Lead Capture; no redundancy or channel diversification yet.
6. **Owner comprehension of settings** — Notification thresholds and qualification concepts leak internal vocabulary.
7. **Mobile inbox polish** — Owners on site; inbox must be flawless on phone — bar is 10/10 responsiveness.
8. **No systematic AI evaluation** — Quality judged ad hoc, not regression-tested on scenario suite.
9. **Embed friction** — Copy-paste snippet only; no CMS plugins or agency playbook in product.
10. **Support burden** — Low-tech users depend on human help for embed, DNS, and email setup.

---

# Biggest Opportunities

Sorted by business impact (highest first).

1. **Close the website → inquiry loop in product** — Verify embed, celebrate first live inquiry, not test chat alone.
2. **Handwerk-vertical depth** — Sanitär/Dach/Elektro-specific prompts, urgency handling, and demo scenarios that feel native.
3. **Inbox excellence** — Cards, one-tap call/email, plain-language priority — owner acts in under 30 seconds.
4. **Honest onboarding** — Server-tracked milestones; clear distinction between setup, test, and live.
5. **Notification reliability** — Right message, right time, with dashboard link; never miss a contactable emergency.
6. **Widget install simplification** — WordPress plugin, agency one-pager, video for non-technical owners.
7. **Time-to-first-value under 30 minutes** — Signup to live embed without human support.
8. **Pilot case studies** — Named trades with real inquiry counts and saved jobs — sales and product fuel.
9. **AI handoff quality** — Structured summary every time: name, need, urgency, contact, location.
10. **German market dominance** — Own "KI-Mitarbeiter für Handwerk" before horizontal players localize.
11. **Self-serve production signup** — When provisioning is safe and automated.
12. **Speed perception** — Stable dashboard shells, caching, no spinner regression on tab switch.
13. **Trust packaging** — DSGVO-ready defaults, professional widget chrome, Impressum-aligned disclosures.
14. **Pricing tied to captured value** — Simple plans aligned with inquiry volume or business size.
15. **Agency channel** — Web agencies that maintain Handwerk sites become distribution.
16. **Urgency-aware routing** — Notfall Sanitär treated differently from quote requests in copy and notifications.
17. **Repeat inquiry recognition** — Returning visitors on same site recognized without annoying re-asks.
18. **WhatsApp as second channel** — High-intent in DACH; model layer partially anticipates this.
19. **Operational metrics for owners** — Response time, missed inquiries — only if it drives callback behavior.
20. **EU expansion after DE proof** — AT/CH copy and legal variants once German pilots retain.

---

# Current Roadmap

Major milestones only. Sequencing follows `PRODUCT_CONSTITUTION.md` priority: activation → comprehension → speed → trust → scale.

| Phase | Milestone | Outcome |
|-------|-----------|---------|
| **Now — Pilot-ready** | Honest activation loop | Owner can embed, verify live widget, receive real inquiry in inbox |
| **Now — Pilot-ready** | Inbox v1 world-class | Cards, contact actions, plain DE/EN, mobile-perfect |
| **Now — Pilot-ready** | Notification path proven | Resend live on pilots; owner alerted on contactable inquiries |
| **Next — First 10 pilots** | Vertical proof | 3+ trades with retained usage and documented saved jobs |
| **Next — First 10 pilots** | Self-serve production signup | No CLI required for standard tenant |
| **Next — First 10 pilots** | AI evaluation harness | Regression suite on German service scenarios |
| **Then — Scale** | Embed distribution | WordPress/common CMS path; agency kit |
| **Then — Scale** | Second channel | WhatsApp or email inbound — only if web loop is undeniable |
| **Then — Scale** | Team features | Multiple users per company with simple roles |
| **Later — Market** | EU Handwerk expansion | AT/CH; vertical marketing |
| **Explicitly not now** | CRM, pipelines, automation builder | Per constitution — out of scope until core loop dominates |

---

# Definition of World-Class

We dominate when a service business owner in Germany says: *"I would not run my website without it"* — the way they already say that about their phone.

**Activation:** A new customer embeds on a live site in one session without calling support. The product detects the first real visitor inquiry and confirms it clearly.

**AI quality:** Every handoff is contactable and actionable. The owner never reads a raw transcript to understand the job. The agent never invents prices, appointments, or commitments. German trades context is native, not translated.

**Inbox:** Opening the dashboard on a phone between jobs feels faster than checking voicemail. One glance: who, what, how urgent, tap to call. Zero training.

**Trust:** DSGVO-respectful by default. Professional on the customer's website. Honest about what is live vs test. Data never crosses tenants.

**Speed:** Sub-second perceived navigation. Notifications arrive before the owner would have checked email anyway.

**Business fit:** Pricing is obvious. Retention follows weekly inquiry value, not contract inertia. We deepen in Handwerk — not spread thin as generic chat software.

**Scale:** Ten thousand tenants on the same architecture without CRM bloat. Channels (web, then messaging) share one inquiry pipeline and one inbox mental model.

**The bar:** Not "better demo than competitors." **Missed jobs recovered.** That is the metric that wins the market.

---

*Update this playbook when modules, milestones, or top risks materially change. Principles live in `PRODUCT_CONSTITUTION.md`; execution standards live in `AGENTS.md`.*
