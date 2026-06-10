import Link from "next/link";

import { MarketingShell } from "@/components/marketing-shell";

const FEATURES = [
  {
    title: "Website widget",
    description:
      "Embed a chat widget on your site. Visitors talk naturally while the agent captures lead details.",
  },
  {
    title: "Smart qualification",
    description:
      "Leads are scored and marked contactable or qualified before your team is notified.",
  },
  {
    title: "Email alerts",
    description:
      "Get Resend-powered notifications with lead summary, score, and a dashboard link.",
  },
  {
    title: "Team dashboard",
    description:
      "Review leads, update status, and manage company settings from one place.",
  },
];

export function LandingPage() {
  return (
    <MarketingShell>
      <section className="hero shell">
        <div className="hero-copy">
          <p className="eyebrow">Pilot-ready lead capture</p>
          <h1>Turn website conversations into qualified leads.</h1>
          <p className="hero-lead">
            Deploy an AI lead capture agent on your website, qualify inbound
            requests automatically, and notify your team when a lead is worth
            following up.
          </p>
          <div className="hero-actions">
            <Link href="/onboarding" className="button button-lg">
              Start your pilot
            </Link>
            <Link href="/login" className="button secondary button-lg">
              Sign in
            </Link>
          </div>
        </div>
        <div className="hero-card card">
          <h2>What you get on day one</h2>
          <ul className="hero-list">
            <li>Embeddable website widget</li>
            <li>Lead scoring and qualification</li>
            <li>Dashboard for your team</li>
            <li>Email notifications via Resend</li>
          </ul>
        </div>
      </section>

      <section className="feature-grid shell">
        {FEATURES.map((feature) => (
          <article key={feature.title} className="feature-card card">
            <h3>{feature.title}</h3>
            <p className="muted">{feature.description}</p>
          </article>
        ))}
      </section>

      <section className="cta-band shell">
        <div className="cta-card card">
          <h2>Ready for your first pilot customer?</h2>
          <p className="muted">
            Create a company, add your admin user, copy the widget snippet, and
            send a test message in under ten minutes.
          </p>
          <Link href="/onboarding" className="button">
            Create pilot account
          </Link>
        </div>
      </section>
    </MarketingShell>
  );
}
