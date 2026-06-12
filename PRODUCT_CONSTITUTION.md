# Product Constitution

**Non-negotiable principles for building the best AI employee for service businesses.**

This document guides product decisions for the next decade. It does not describe features or implementation. For engineering standards, see `AGENTS.md`.

When principles conflict, use the [Decision Framework](#decision-framework).

---

## Mission

Build an AI employee that captures, understands, and hands off website inquiries for service businesses — so owners never lose a job because they were on site, in a meeting, or asleep.

We start where the pain is sharpest: small trades and local service companies (1–20 people) who live by phone, reputation, and response time.

We measure success by whether a business gets **contactable, complete, actionable inquiries** from real customers — and acts on them without training or IT help.

---

## Customer Promise

To every business owner who trusts us:

1. **You will not miss serious inquiries** from your website when we are active.
2. **You will understand each inquiry in seconds** — who, what, urgency, how to reach them.
3. **You stay in control** — the AI assists; you decide whom to call and when.
4. **We are honest** — we never claim success we have not earned (demo ≠ live, test ≠ production).
5. **We respect your customers' data** — lawful, minimal, professional.

If we cannot keep a promise, we do not imply it.

---

## Product Principles

1. **One job.** Capture and qualify inbound interest. Everything else is in service of that job or out of scope.
2. **The customer's customer comes first.** End-user experience on the business's website is part of the product, not an afterthought.
3. **Inbox, not admin panel.** Owners think in *Anfragen* and phone calls, not pipelines, scores, or configuration trees.
4. **Plain language over jargon.** If a Handwerker would not say it, we do not show it.
5. **Hide machinery.** Slugs, IDs, model names, and internal states stay internal unless the owner truly needs them.
6. **Activation before expansion.** First real inquiry on a real website beats the tenth dashboard setting.
7. **One high-impact improvement beats five small ones.** Ship what moves the core loop.

---

## UX Principles

1. **Answer five questions on every screen:** What does the user want? Fewer clicks? More confidence? Less cognitive load? One moment of delight?
2. **One primary action per screen.** Secondary actions stay visually and cognitively subordinate.
3. **Calm and competent.** Like a reliable office assistant — not a sci-fi control room.
4. **Progressive disclosure.** Advanced options exist; they do not block the first hour of use.
5. **Honest states.** Empty, loading, error, and success must tell the truth and suggest the next step.
6. **Mobile is not optional.** Owners check inquiries on phones between jobs.
7. **German-first, English-equal.** Copy parity is a product requirement, not a translation pass.

Minimum bar for any UI we ship: UX and visual design ≥ 9.5/10, accessibility ≥ 9/10, performance ≥ 9.5/10, responsiveness 10/10.

---

## AI Quality Principles

1. **Useful handoff, not clever chat.** The output is a request a human can act on — not a transcript to interpret.
2. **Extract before embellish.** Name, need, urgency, contact method, location — structured truth matters more than fluency.
3. **Ask only what unlocks action.** Every question must reduce uncertainty for the business or improve reachability.
4. **Fail gracefully.** When uncertain, say so plainly; never invent facts, prices, appointments, or commitments.
5. **Respect the trade.** Answers reflect how service businesses actually work — urgency, geography, callbacks, no-shows.
6. **Human tone, bounded authority.** Warm and professional; never impersonate the owner or bind them contractually.
7. **Quality is measured on real scenarios.** Sanitär at 22:00, Dach after a storm, Elektro with a partial address — not demo scripts alone.

---

## Trust Principles

1. **Data minimization.** Collect and retain only what serves inquiry capture and handoff.
2. **Lawful by design.** DSGVO and local requirements are constraints at design time, not legal review at the end.
3. **Tenant isolation is sacred.** One business never sees another's inquiries, settings, or customers.
4. **No dark patterns.** No fake urgency, hidden costs, or success theater.
5. **Transparency on AI.** Customers of our customers should know they are speaking with an assistant when law or context requires it.
6. **Professional presence.** Our touchpoints must not embarrass a serious local business.
7. **Security is part of the product.** Breach of trust ends the relationship — treat it accordingly.

---

## Speed Principles

1. **Time to first real inquiry is the north star.** Every onboarding step must justify its cost in minutes-to-value.
2. **Response perceived as instant.** Visitors do not wait; owners do not stare at spinners.
3. **Default to the fast path.** Setup, inbox, and contact actions require minimal steps.
4. **Speed without lies.** Fast must not mean "looks done" when it is not.
5. **Operational speed for the owner.** From notification to callback should be shorter than without us.
6. **Defer scale problems until pilots have scale.** Optimize for the first 100 inquiries, not hypothetical millions — but never ship slowness we cannot fix.

---

## Business Model Principles

1. **Value follows captured revenue opportunities.** We win when owners win jobs they would have lost.
2. **Simple pricing.** A owner must understand the bill in one conversation.
3. **No incentive to hoard attention.** We do not optimize for chat volume; we optimize for qualified, contactable inquiries.
4. **Land with one trade, expand with proof.** Depth in one vertical beats shallow coverage of ten.
5. **Retention is earned weekly.** If inquiries stop being useful, we have no right to the subscription.
6. **Partnerships serve the owner.** Agencies and integrators are channels, not the product strategy.
7. **Sustainable unit economics.** Growth that destroys margin or support quality is not growth.

---

## What We Will Not Build

Until the core loop is undeniable for pilots, we will not build:

- **A general CRM** — pipelines, deal stages, forecasting, automation builders
- **A website builder** — we integrate with where sites already live
- **A replacement for the phone** — we route humans to calls, not replace them
- **An AI that commits on behalf of the business** — no binding quotes, appointments, or contracts without explicit human approval
- **Enterprise complexity for micro-businesses** — roles, permissions matrices, multi-brand admin for its own sake
- **Feature parity chasing** — copying incumbents because they have a checkbox
- **Developer-first products** — APIs and webhooks serve the product; they are not the product
- **Vanity AI** — demos, avatars, or novelty that do not improve inquiry quality
- **Success theater** — metrics, badges, or onboarding steps that celebrate activity instead of real inquiries

If a request belongs on this list, the answer is no — or not yet, with a written reason.

---

## Decision Framework

Use this order when choosing what to build, ship, or kill.

### 1. Does it strengthen the core loop?

```
Visitor on business website → inquiry captured → owner understands → owner contacts customer
```

If no, deprioritize unless it removes a proven blocker to step one.

### 2. Does it improve activation, comprehension, or trust?

| Pillar | Question |
|--------|----------|
| **Activation** | Does a new customer reach a real website inquiry faster or more reliably? |
| **Comprehension** | Can the owner act without explanation, support, or IT? |
| **Trust** | Would we stake our name on this behavior in front of their customers? |

If none apply, do not ship.

### 3. Is it the simplest solution to the root problem?

Reject symptom fixes. Reject scope that bundles unrelated wins. Prefer deletion over addition.

### 4. Would we be proud in a pilot's shop?

If a Sanitärmeister would find it confusing, cheesy, or risky, it does not ship.

### 5. One-way door?

Reversible decisions: decide fast. Hard-to-reverse decisions (pricing, data use, AI commitments, brand promise): slow down, document, align with this constitution.

### Default answers

| Situation | Answer |
|-----------|--------|
| Feature vs. polish on core loop | Core loop |
| Breadth vs. depth in one trade | Depth |
| Owner dashboard vs. end-customer experience | Whichever is the current bottleneck — usually whichever breaks the loop |
| Build vs. integrate | Integrate if good enough; build only if it is the product |
| Ship now vs. ship right | Ship right if trust is at stake; ship now if learning is blocked |

---

*This constitution overrides roadmaps, opinions, and urgency. Change it rarely and deliberately — not to excuse shortcuts.*
