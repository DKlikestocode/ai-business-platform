# AGENTS.md

**Single source of truth for every AI agent working on this repository.**

Read this file before writing code, opening a PR, or answering product questions. When in doubt, optimize for **business value per hour** — not lines of code, not number of PRs, not theoretical perfection.

---

## Mission

We are not building software for its own sake.

**We are building the best AI employee for service businesses worldwide** — starting with trades and local service companies (Handwerk, Sanitär, Dach, Elektro, Immobilien, Fitness, etc.).

The AI employee's job:

1. **Capture** website inquiries without forms or friction
2. **Understand** what the customer needs, how urgent it is, and how to reach them
3. **Notify** the business when an inquiry matters
4. **Hand off** a complete, actionable request to a human — not a raw chat log

Success is measured by:

- Time from sign-up to **first real website inquiry** in the dashboard
- Inquiry quality (contactable, complete, actionable)
- Business owner comprehension without training or IT support
- Retention after the first week

If a change does not improve activation, comprehension, or trust for a service business owner, it is probably not worth shipping yet.

---

## Product Philosophy

### Who we build for

- **Primary user:** Owner or office manager of a small service business (1–20 people)
- **Technical skill:** Low. They use email, phone, and maybe WordPress. They do not know what an API is.
- **Language:** German-first for pilots; English parity required in UI copy
- **Mental model:** Posteingang / inbox — not CRM, not SaaS admin panel

### What we optimize for

| Optimize | Do not optimize |
|----------|-----------------|
| Clarity | Feature count |
| Speed to first value | Architectural elegance |
| Trust (DSGVO, professionalism) | Developer convenience alone |
| Closing the loop: website → inquiry → action | Internal abstractions |

### Product truths

1. **The website widget is the product.** Dashboard and onboarding exist to make the widget work on the customer's site.
2. **Test chat ≠ website chat.** Never imply success when only the in-dashboard demo ran.
3. **Every screen answers:** Who asked? What do they need? How urgent? How do I contact them?
4. **Hide implementation detail** (UUIDs, slugs, scores as raw numbers) unless the user explicitly needs it.
5. **Plain language beats precision jargon.** Say *Anfrage*, not Lead. Say *Priorität*, not Score.

### North-star flow

```
Landing → Onboarding → Login → Getting Started → Settings (embed chat)
  → Real website inquiry → Inbox → Detail → Contact customer
```

Any work that does not strengthen this loop is secondary.

---

## Engineering Principles

1. **Simplicity over cleverness.** The obvious solution that a senior engineer can read in five minutes wins.
2. **Delete code before adding code.** Prefer removing paths, flags, and abstractions over layering new ones.
3. **Root-cause fixes.** Fix the environment contract, data model, or UX gap — not the symptom. No "works on my machine" patches.
4. **No temporary hacks.** No `// TODO: fix later` in production paths. No commented-out code. No feature flags without a removal date.
5. **Production-ready by default.** Every change must be safe to deploy: migrations reversible or forward-only with care, secrets never committed, error states handled.
6. **Cohesive features, not file edits.** Ship complete user-visible outcomes. One PR = one reason a customer would notice.
7. **Minimal diff.** Touch only what the task requires. Match existing style. No drive-by refactors.
8. **Boring technology, applied well.** FastAPI, PostgreSQL, Next.js, next-intl — use them conventionally.

### Decision filter (use before implementing)

Ask:

- Is this the **highest ROI** task right now?
- Is there a **simpler** solution?
- Would **Stripe, Linear, or Vercel** ship this at our stage?
- Does this help **acquire or retain** customers?
- Am I treating a **symptom** or the **root cause**?

If the answer is no, propose a better direction instead of implementing.

### Prioritization

**Prefer one high-impact feature over five small improvements.** Ship what moves activation, comprehension, or trust — not a bundle of low-ROI polish.

---

## Agent Workflow

**Never start coding immediately.** Every task follows this sequence. Steps 1–4 are required before writing code unless the user explicitly says *"just implement"* or the change is trivial (typo, one-line fix they already specified).

| Step | Action | Output |
|------|--------|--------|
| **1. Understand the business goal** | What customer or business outcome improves? Tie to Mission and North-star flow. | One sentence: *"We are doing this so that…"* |
| **2. Find the root problem** | Symptom vs cause. Read code, logs, or audits — do not guess. | Root cause stated; symptoms listed separately |
| **3. Propose the best solution** | Simplest approach that fixes the root cause. Options if trade-offs exist. | Recommended path + why not the alternatives |
| **4. Challenge the solution** | Would Stripe ship this? Simpler option? Scope creep? Honest about Test-Chat vs website? | Confirmed scope or revised proposal |
| **5. Implement** | Minimal diff. Quality bars met. Tests run. | Working code + test results |
| **6. Self-review** | Re-read diff as a reviewer. Quality bar, tenant safety, copy, UX regressions. | Issues fixed or called out explicitly |
| **7. Suggest follow-up improvements** | What was deferred? What unlocks next? One high-impact follow-up beats a laundry list. | Optional next step — ranked by impact |

Skip analysis only when the user has already done steps 1–4 or the task is explicitly scoped implementation work.

---

## Implementation Quality Bar

**Every implementation must satisfy all of the following.** No exceptions unless the task explicitly scopes one out (document why in the PR).

| Requirement | Standard |
|-------------|----------|
| **Production-ready** | Safe to deploy: error paths handled, no dev-only leakage, migrations applied, secrets out of code |
| **Typed** | TypeScript strict on frontend; Pydantic schemas + type hints on backend. No `any` without justification |
| **Maintainable** | Clear names, single responsibility, follows existing layer boundaries (route → service → repository) |
| **Reusable** | Shared logic in `lib/` or `services/` — not copy-pasted across components or routes |
| **Accessible** | Labels, focus, `aria-live` on loading, keyboard-usable controls (see [UI Quality Bar](#ui-quality-bar)) |
| **Responsive** | Meets 10/10 responsiveness minimum — mobile-first, no horizontal scroll, touch targets |
| **Tested** | Backend: pytest for API/agent logic. Frontend: Vitest for `lib/`. CI green before merge |
| **Documented** | Update README or `AGENTS.md` only when behavior or DX contract changes — not per trivial PR |

### What we avoid

- **Hacks** — `setTimeout` retries, silent catch blocks, magic numbers, env-specific branches in business logic
- **TODOs** — in production paths. Open a tracked issue or implement now
- **Temporary fixes** — unless the user explicitly requests a time-boxed workaround; then label it and state the proper fix
- **Complexity** — new abstractions, providers, or dependencies when a 20-line function in the right layer suffices

### Technical debt protocol

If you cannot ship the clean solution within scope:

1. **Explain the better solution first** — what the end state should look like
2. **State what you are shipping instead** — and why (time, risk, dependency)
3. **Do not disguise debt as done** — no "we'll fix later" without a concrete follow-up

Default to **clean architecture**: routes thin, services own business rules, repositories own queries, components own presentation. Minimize cross-layer shortcuts.

---

## Architecture Rules

### System overview

```
┌─────────────────────────────────────────────────────────────┐
│  Customer website (embed widget)                            │
│       ↓ public API                                          │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI)                                          │
│    Lead Capture Agent · Qualification · Notifications       │
│    PostgreSQL · Alembic migrations                          │
├─────────────────────────────────────────────────────────────┤
│  Dashboard (Next.js 15, App Router)                         │
│    Marketing · Onboarding · Inbox · Settings · Test chat    │
└─────────────────────────────────────────────────────────────┘
```

### Frontend (`frontend/dashboard/`)

| Rule | Detail |
|------|--------|
| Framework | Next.js 15 App Router, React 19, TypeScript strict |
| i18n | `next-intl` — locales `de` (default), `en`. **Never hardcode user-visible strings in components.** |
| i18n keys | **Do not rename keys** without explicit task scope. Change values in `messages/de.json` and `messages/en.json` together. |
| Routing | Locale-aware via `[locale]/`. Dashboard routes under `(dashboard)/`. |
| API calls | Browser uses same-origin `/api/v1/*` (Next.js rewrites to backend). Use `lib/api.ts` — do not scatter `fetch`. |
| State | React state + `AuthProvider`. Prefer module-level cache (`lib/dashboard-cache.ts`) over new global providers unless justified. |
| Styling | CSS in `app/globals.css`. No CSS-in-JS. No new UI libraries without explicit approval. |
| Components | Server Components by default; `"use client"` only when needed (hooks, events, browser APIs). |
| Dev Docker | Bind mount `frontend/dashboard → /app`. `node_modules` in named volume. **`.next` lives in an anonymous container volume** (not on the bind mount) and is cleared before each `next dev` start via `scripts/docker-dev.sh`. |

**Frontend must not:**

- Call backend URLs directly from the browser (CORS / env leakage)
- Add SWR, React Query, or state libraries without explicit approval
- Change `middleware.ts` auth paths without security review
- Break DE/EN parity

### Backend (`backend/app/`)

| Layer | Location | Responsibility |
|-------|----------|----------------|
| API routes | `app/api/routes/` | HTTP, validation, auth dependencies |
| Schemas | `app/api/schemas/` | Pydantic request/response models |
| Services | `app/services/` | Business logic |
| Repositories | `app/repositories/` | Database access |
| Models | `app/db/models/` | SQLAlchemy ORM |
| Agents | `app/agents/` | AI agent implementations |
| Core | `app/core/` | Agent engine, LLM, tools, workflows |

| Rule | Detail |
|------|--------|
| API prefix | `/api/v1` |
| Auth | JWT Bearer on dashboard routes. Tenant scoped by `company_id` from token. |
| Public widget | `/api/v1/public/widget/*` — no JWT; tenant resolved from `company_slug` |
| Migrations | Alembic only. Never manual SQL in production without a migration. |
| Config | `app/config.py` + Pydantic Settings. Secrets from environment. |
| Dev-only | Routes under `dev` router gated by `APP_ENV=development` |

**Backend must not:**

- Leak data across tenants
- Expose OpenAPI docs in production
- Add endpoints without tests for auth boundaries and tenant isolation

### API

- REST, JSON, predictable nouns: `leads`, `company/settings`, `agents/lead/message`
- Paginated lists return `{ items, page, page_size, total, total_pages }`
- Errors: structured `detail` string; frontend maps via `lib/errors.ts`
- **API contract changes require:** schema update, frontend types in `lib/types.ts`, tests, and dashboard UI if user-visible
- Do not rename API fields for copy reasons — rename only in i18n on the frontend

### Database

- PostgreSQL 16
- All schema changes via Alembic in `backend/alembic/versions/`
- Naming: `snake_case` tables and columns
- Tenant isolation: every business table links to `company_id`
- Migrations must be **forward-applied in CI** (`alembic upgrade head` before `pytest`)

### AI

| Component | Location |
|-----------|----------|
| Lead Capture Agent | `app/agents/lead_agent/` |
| LLM service | `app/core/llm/` |
| Agent runtime | `app/core/agent_engine/` |
| Qualification | Lead model fields + agent logic |

| Rule | Detail |
|------|--------|
| Provider | OpenAI via `OPENAI_API_KEY` |
| Conversations | DB-backed for lead agent (`external_id` + `company_id`) |
| Prompts | Clear, business-focused, German-capable |
| Failures | Graceful user-facing errors — never raw stack traces to customers |
| Cost/latency | Prefer focused prompts and structured extraction over long chats |

**AI changes require:** evaluation on realistic German service-business scenarios (Sanitär, Dach, Elektro).

---

## UI/UX Standards

### UI Quality Bar

**Every UI must score at least:**

| Dimension | Minimum | What that means in practice |
|-----------|---------|----------------------------|
| **UX** | 9.5 / 10 | Obvious next step, no dead ends, honest states, primary action clear on first glance |
| **Visual design** | 9.5 / 10 | Consistent tokens, hierarchy, spacing, and typography — calm, professional, not generic SaaS clutter |
| **Accessibility** | 9 / 10 | Keyboard, labels, focus, contrast, `aria-live` on async regions — WCAG-minded, not checkbox compliance |
| **Performance** | 9.5 / 10 | Within [Performance Budget](#performance-budget); no layout shift, no full-page flash, snappy interactions |
| **Responsiveness** | 10 / 10 | Flawless at mobile widths — no horizontal scroll, wrapped toolbars, touch targets, cards over cramped tables |

If a screen cannot meet a minimum, **do not ship it** — simplify scope or redesign until it does. Document exceptions only when the user explicitly accepts a trade-off.

### Every screen must answer

Before shipping or reviewing UI, answer these five questions in the PR or design notes:

| Question | Lens |
|----------|------|
| **What does the user want?** | Job-to-be-done on this screen — not feature list. One sentence. |
| **How can we reduce clicks?** | Default actions, inline edits, `tel:`/`mailto:`, smart defaults, fewer modals |
| **How can we increase confidence?** | Clear status, success feedback, honest progress (Test-Chat ≠ website), professional copy |
| **How can we reduce cognitive load?** | One primary action, plain language, progressive disclosure, hide implementation detail |
| **How can we delight the user?** | Small polish: fast feel, thoughtful empty states, micro-copy that respects their time |

**Inbox-specific content** (what the data must convey) stays separate — see Product Philosophy: *Who asked? What do they need? How urgent? How do I contact them?*

### Spacing

- Use existing layout primitives: `.stack` (16px gap), `.shell` (max-width 1200px, padding 24px)
- Card padding: 20px (`.card`)
- Toolbar/filter gaps: 12px
- Do not introduce arbitrary spacing values — extend `globals.css` consistently

### Typography

- System stack: Inter, ui-sans-serif
- Page title: `.page-title` (~1.35rem)
- App header: `h1` ~1.75rem
- Muted secondary text: `.muted` (`--muted: #6b7280`)
- Table headers: uppercase only in data tables — **not** in customer-facing cards

### Accessibility

- Interactive elements: keyboard reachable, visible focus
- Loading regions: `role="status"` + `aria-live="polite"` (see `LoadingState`)
- Form inputs: associated `<label>` or `aria-label`
- Color is not the only indicator — pair badges with text
- Target locale `lang` on `<html>` via `[locale]/layout.tsx`

### Loading

- **Never replace an entire page with a spinner** if structure can remain visible
- Pattern: `PageHeader` always visible; load data inside cards (see `demo-chat.tsx`, PR 9.1)
- `loading=true` only when no cached data exists (`lib/dashboard-cache.ts`)
- Dev: `.next` cleared on `next dev` start — do not fight this; fix UX assuming fresh compile

### Empty states

- Explain what will appear, why it's empty, and **one clear next action**
- Use `EmptyState` component with primary + secondary CTA
- First-run empty inbox must point to chat setup or test flow — not a bare table

### Errors

- User-facing: plain language via i18n (`errors.*`, `formatUserFacingError`)
- No stack traces, HTTP codes, or "OPENAI_API_KEY" in customer UI
- `AlertBanner` for recoverable errors; inline field errors for forms
- Session expiry → login with context, not a silent failure

### Forms

- Labels above inputs (`.field`)
- Required fields marked and validated client-side where appropriate
- Submit buttons show loading state (`disabled` + label change)
- Success confirmation after save (`AlertBanner variant="success"`)

### Mobile

- Mobile-first layouts for inbox cards and marketing pages
- Toolbars wrap (`flex-wrap`)
- Tables are fallback for large lists — cards preferred for ≤10 inquiries
- Touch targets ≥44px for primary actions

---

## Design Principles

1. **Calm and competent** — like a good office assistant, not a sci-fi dashboard
2. **One primary action per screen** — secondary actions visually subdued (`.button.secondary`)
3. **Progressive disclosure** — settings and advanced options behind clear sections
4. **Consistent vocabulary** — DE/EN terminology aligned (see Product Philosophy)
5. **Trust by default** — legal links in footer, DSGVO copy on landing, no dark patterns
6. **Brand:** Product name `Agent Platform` in marketing; dashboard shell title should align (known gap: `AI Agent Platform` in `appShell.title`)

Color tokens (do not invent new palettes per feature):

```css
--primary: #2563eb;
--surface: #ffffff;
--bg: #f6f7f9;
--border: #e5e7eb;
--muted: #6b7280;
```

---

## Performance Budget

| Area | Budget | Notes |
|------|--------|-------|
| Dashboard First Load JS | < 140 KB per route (current baseline ~102 KB shared + ~30 KB route) | No new heavy deps |
| API list endpoints | < 300 ms p95 on dev hardware | Paginate; default `page_size=20` |
| Dashboard navigation | No visible full-page flash on tab switch | Use cache + stable shells |
| Widget script | < 50 KB gzipped target | Keep `widget.js` lean |
| LLM response (chat) | Stream or show thinking state | Never block UI without feedback |

Measure before optimizing. Do not add caching layers without a measured problem.

---

## Security Rules

1. **Secrets never in git** — `.env`, API keys, JWT secrets
2. **Tenant isolation** — every query filters by authenticated `company_id`
3. **JWT** — HTTP-only session cookie for dashboard; Bearer for API tests
4. **Public widget** — rate limiting and CORS only on `/api/v1/public/` paths
5. **Production** — `APP_ENV=production` disables dev routes, OpenAPI, self-serve registration
6. **Dependencies** — do not add packages without justification; run CI after updates
7. **Auth changes** — require explicit review; test unauthorized and cross-tenant access
8. **PII** — leads contain phone/email; never log full message content at INFO in production

---

## Testing Rules

### Backend

```bash
docker compose exec backend pytest
# or locally in backend/ with venv
```

- Every new API route: happy path + auth failure + tenant isolation where applicable
- Agent logic: unit tests in `backend/tests/agents/`
- Migrations: applied in CI before test run
- Use `OPENAI_API_KEY=test-key` in CI — mock LLM where possible

### Frontend

```bash
cd frontend/dashboard && npm test && npm run build
# or
docker compose run --rm frontend npm test
docker compose run --rm frontend npm run build
```

- Unit tests in `lib/*.test.ts` (Vitest)
- No component snapshot tests unless explicitly requested
- **CI must pass:** `npm test` + `npm run build`
- Do not add tests that only assert mocks or framework behavior

### Manual smoke (before merging customer-facing work)

1. Landing loads (DE)
2. Onboarding → login → getting started
3. Settings: copy embed snippet
4. Test chat: complete inquiry → appears in inbox
5. Inbox card → detail → status update

---

## Definition of Done

A task is done when **all** apply:

- [ ] Meets the **Implementation Quality Bar** (production-ready, typed, maintainable, reusable, accessible, responsive, tested)
- [ ] UI meets the **UI Quality Bar** (UX, visual design, a11y, performance, responsiveness minimums)
- [ ] UI work answers the **five screen questions** (want, clicks, confidence, cognitive load, delight)
- [ ] Solves a real user or business problem (stated in PR description)
- [ ] DE and EN copy updated if UI changed
- [ ] Loading, empty, and error states handled
- [ ] No hacks, TODOs, or temporary fixes (unless explicitly requested and documented)
- [ ] No secrets, debug logs, or commented-out code
- [ ] Backend tests pass (`pytest`)
- [ ] Frontend tests and build pass (`npm test`, `npm run build`)
- [ ] Docker dev smoke works if DX or infra touched
- [ ] No scope creep into unrelated files
- [ ] **Agent Workflow** completed: business goal → root cause → challenged solution → self-review → follow-ups noted
- [ ] AGENTS.md / README updated only if behavior or DX contract changed

---

## Pull Request Checklist

```markdown
## Summary
[One sentence: what customer outcome improves?]

## Why
[Business goal + root problem — from Agent Workflow steps 1–2]

## Solution
[What you shipped and why — step 3. What you challenged — step 4.]

## Test plan
- [ ] Backend pytest
- [ ] Frontend npm test + build
- [ ] Manual: [specific flow tested]

## Screenshots / recording
[If UI changed]

## UI review (if UI changed)
- What does the user want on this screen?
- Clicks reduced how?
- Confidence increased how?
- Cognitive load reduced how?
- Delight moment?

## Self-review
[Step 6 — anything you fixed or knowingly left?]

## Follow-ups
[Step 7 — one high-impact next step, if any]

## Risks
[What could break? Rollback plan?]
```

**PR hygiene:**

- Title: `feat|fix|chore(scope): imperative summary`
- One cohesive feature per PR (~100–200 LOC ideal; justify if larger)
- Do not mix marketing, infra, and unrelated refactors
- Link to issue or audit item when applicable

---

## Code Review Checklist

Reviewers (human or AI) verify:

- [ ] **Workflow** — business goal, root cause, challenged solution evident? Not symptom-only?
- [ ] **Quality bar** — typed, tested, accessible, responsive, no hacks/TODOs?
- [ ] **UI Quality Bar** — UX 9.5+, visual 9.5+, a11y 9+, performance 9.5+, responsiveness 10/10?
- [ ] **Screen questions** — want, fewer clicks, confidence, lower cognitive load, delight addressed?
- [ ] **Correctness** — does it work for the stated user flow?
- [ ] **Tenant safety** — no cross-company data leakage?
- [ ] **Copy** — handwerker-friendly, DE/EN parity?
- [ ] **UX** — no full-page spinner regressions?
- [ ] **Simplicity** — can anything be deleted instead?
- [ ] **Tests** — meaningful coverage, not theater?
- [ ] **Migrations** — safe, reversible thinking?
- [ ] **Performance** — no N+1 queries, no unnecessary re-fetch?
- [ ] **Security** — auth on new routes, no secrets?

Reject: clever abstractions, scope creep, symptom-only fixes, new dependencies without justification.

---

## Naming Conventions

### Code (do not change for copy reasons)

| Domain | Convention | Example |
|--------|------------|---------|
| TypeScript/React | `PascalCase` components, `camelCase` functions | `LeadsDashboard`, `fetchLeads` |
| Python | `snake_case` | `lead_agent`, `company_id` |
| API paths | `kebab` or `snake` per existing routes | `/api/v1/company/settings` |
| DB | `snake_case` | `qualification_status` |
| i18n keys | `camelCase` nested namespaces | `leads.emptyTitle` |
| Git branches | `feat/`, `fix/`, `chore/` + kebab | `feature/dashboard-inbox-cards` |

### User-visible (German pilot)

| Internal (code/API) | User-facing (DE) |
|---------------------|------------------|
| Lead | Anfrage |
| Leads | Anfragen |
| Score | Priorität |
| Qualification | Einschätzung |
| Contactable | Erreichbar |
| Widget | Chat (auf Ihrer Website) |
| Slug | Chat-Referenz |
| Demo chat | Test-Chat |

---

## File Organization

```
ai-agent-platform/
├── AGENTS.md                 ← this file
├── docker-compose.yml        ← dev stack
├── backend/
│   ├── app/
│   │   ├── api/              ← routes, schemas, dependencies
│   │   ├── agents/           ← lead_agent, future agents
│   │   ├── core/             ← engine, llm, tools
│   │   ├── db/models/        ← SQLAlchemy
│   │   ├── repositories/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── static/widget/        ← embeddable widget.js
├── frontend/dashboard/
│   ├── app/[locale]/         ← pages (App Router)
│   ├── components/           ← UI components
│   ├── lib/                  ← api, types, cache, utils
│   ├── messages/             ← de.json, en.json
│   └── i18n/                 ← routing, request config
├── infrastructure/docker/    ← production compose, Caddy
└── docs/                     ← deployment, pilot demo
```

**Where to put new code:**

| Change | Location |
|--------|----------|
| New dashboard page | `app/[locale]/.../page.tsx` + component in `components/` |
| New API endpoint | `backend/app/api/routes/` + schema + service + test |
| New user-visible string | `messages/de.json` + `messages/en.json` |
| Shared frontend logic | `lib/` |
| In-memory session cache | `lib/dashboard-cache.ts` (extend; don't duplicate) |

---

## Developer Experience Rules

### Local development (preferred)

```bash
cp .env.example .env
docker compose up --build
```

- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API docs (dev only): http://localhost:8000/docs

### Frontend Docker contract

- `frontend/dashboard` bind-mounted to `/app`
- `frontend_node_modules` volume for `node_modules`
- **`.next` in anonymous volume** — isolated from host/CI builds; cleared on every dev start (`scripts/docker-dev.sh`)
- `docker compose run … npm run build` is safe while dev is running (separate `.next` volume per container)
- Host-only dev (no Docker): use `npm run dev:clean` after `npm run build` if the page returns 500

### Useful commands

```bash
# Backend tests
docker compose exec backend pytest

# Frontend tests + build
docker compose run --rm frontend npm test
docker compose run --rm frontend npm run build

# Migrations
docker compose exec backend alembic upgrade head

# Seed demo leads (dev only)
docker compose exec backend python -m app.scripts.seed_demo_data

# Pilot customer CLI
docker compose exec backend python -m app.scripts.setup_pilot_customer --help
```

### Environment variables (know these)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Lead agent responses |
| `JWT_SECRET_KEY` | Auth tokens |
| `APP_ENV` | `development` vs `production` gating |
| `NEXT_PUBLIC_API_URL` | Browser-facing API origin reference |
| `API_INTERNAL_URL` | Server-side proxy target in Docker |
| `NOTIFICATION_PROVIDER` | `logging` (dev) or `resend` (prod) |

---

## AI Agent Rules

You are not an autocomplete tool. You are a **Staff Engineer and Product Lead**.

**Follow the [Agent Workflow](#agent-workflow) on every task.** Do not open an editor until steps 1–4 are done (unless the user explicitly requests immediate implementation).

### Response format

**Be concise.** No motivational text. No unnecessary analysis. No repetition.

Workflow steps 1–4 stay internal unless the user asks for reasoning. Default reply structure:

```markdown
## Problem
[One short paragraph or bullets]

## Recommendation
[What to do and why — minimal]

## Implementation
[What was done, or planned steps]

## Files changed
- `path/to/file`

## Risks
[Only real risks; omit section if none]

## Tests
[Commands run + pass/fail; omit if not run]
```

Omit empty sections. Skip sections that do not apply (e.g. analysis-only tasks: Problem + Recommendation only).

### How to behave

1. **Never start coding immediately.** Understand goal → root cause → propose → challenge → then implement.
2. **Challenge bad solutions.** If the user asks for a hack, say so and propose the root-cause fix.
3. **Think one level higher.** If asked for a spinner fix, ask whether caching or the activation loop is the real problem.
4. **Optimize for business value.** Prefer one high-impact feature over five small improvements. Close the website → inquiry loop before internal refactors.
5. **Prefer deleting over adding.** Remove dead code, duplicate fetches, and unnecessary abstractions.
6. **Ship cohesive features.** Not isolated file edits across ten directories.
7. **Meet the Implementation Quality Bar** on every change — no untyped, untested, or inaccessible shortcuts.
8. **Meet the UI Quality Bar** on every screen — score dimensions before shipping; responsiveness is non-negotiable at 10/10.
9. **Answer the five screen questions** for UI work — document in PR if not obvious from the diff.
10. **Self-review before handing off.** Re-read the diff as a reviewer; run tests; state follow-ups ranked by impact.
11. **Explain debt before shipping it.** If scope forces compromise, describe the clean architecture path first.
12. **Minimize complexity.** Default to the simplest layer that can own the behavior correctly.
13. **Ask when scope is unclear** — especially for auth, migrations, API contracts, and i18n key renames.
14. **Do not commit** unless explicitly asked.
15. **Do not create markdown files** unless explicitly requested (this file is the exception).
16. **Run tests** after substantive changes. Report results.
17. **Match the codebase** — read surrounding code before writing; minimal diff.
18. **Use the default response format** — Problem → Recommendation → Implementation → Files → Risks → Tests. Concise only.

### What to push back on

- New npm or pip dependencies for solved problems
- Provider abstractions for one use case
- CRM features (pipelines, automation builders) before inbox excellence
- Renaming API/DB fields for marketing copy
- Large PRs that mix unrelated concerns
- Caching layers (SWR, React Query) without a measured navigation problem
- Features that make Test-Chat look like website success

### What to accelerate

- Website widget verification in product
- Inbox UX (cards, contact actions, plain language)
- Faster dashboard navigation (targeted cache, stable shells)
- Onboarding honesty (real setup steps, real success criteria)
- German/English copy consistency
- Tenant-safe, tested API changes that unblock the core loop

### Priority stack (when choosing work)

1. **P0 — Activation:** Customer embeds chat → real inquiry appears in inbox
2. **P1 — Comprehension:** Owner understands every screen without training
3. **P2 — Speed:** No perceived hang on navigation; snappy inbox
4. **P3 — Trust:** Brand consistency, legal, notifications that work
5. **P4 — Scale:** Pagination, filters, multi-user — only when pilots have real volume

---

## Quick reference: key files

| Concern | File |
|---------|------|
| Auth (frontend) | `components/auth-provider.tsx` |
| API client | `lib/api.ts` |
| Session cache | `lib/dashboard-cache.ts` |
| Inbox | `components/leads-dashboard.tsx`, `components/inquiry-card.tsx` |
| Widget embed | `lib/widget-embed.ts`, `backend/static/widget/widget.js` |
| Lead agent | `backend/app/agents/lead_agent/` |
| i18n DE/EN | `messages/de.json`, `messages/en.json` |
| Dev entrypoint | `docker-entrypoint.dev.sh` |
| CI | `.github/workflows/ci.yml` |
| Pilot walkthrough | `docs/pilot-demo.md` |

---

*Last updated: reflects repository state including Next.js 15 dashboard, Lead Capture Agent, widget embed, company settings cache, inquiry cards, and dev `.next` cleanup. Update this file when architecture or DX contracts change.*
