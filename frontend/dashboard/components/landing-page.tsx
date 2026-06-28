import { getTranslations } from "next-intl/server";

import { HeroWebsiteChatPreview } from "@/components/hero-website-chat-preview";
import { LandingComparison } from "@/components/landing-comparison";
import { LandingHowItWorks } from "@/components/landing-how-it-works";
import { LandingIndustries } from "@/components/landing-industries";
import { LandingPublicDemo } from "@/components/landing-public-demo";
import { LandingSocialProof } from "@/components/landing-social-proof";
import { MarketingShell } from "@/components/marketing-shell";
import { PilotBookingLink } from "@/components/pilot-booking-link";
import { Link } from "@/i18n/navigation";

const FEATURE_KEYS = [
  "widget",
  "qualification",
  "email",
  "dashboard",
] as const;

const TRUST_KEYS = ["gdpr", "https", "hosting", "noTraining"] as const;

const TRUST_I18N_KEYS: Record<(typeof TRUST_KEYS)[number], string> = {
  gdpr: "trustGdpr",
  https: "trustHttps",
  hosting: "trustHosting",
  noTraining: "trustNoTraining",
};

function TrustIcon({ name }: { name: (typeof TRUST_KEYS)[number] }) {
  const icons = {
    gdpr: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    https: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect
          x="3"
          y="11"
          width="18"
          height="11"
          rx="2"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path
          d="M7 11V7a5 5 0 0 1 10 0v4"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    ),
    hosting: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <ellipse cx="12" cy="5" rx="9" ry="3" stroke="currentColor" strokeWidth="2" />
        <path
          d="M3 5v6c0 1.66 4.03 3 9 3s9-1.34 9-3V5M3 11v6c0 1.66 4.03 3 9 3s9-1.34 9-3v-6"
          stroke="currentColor"
          strokeWidth="2"
        />
      </svg>
    ),
    noTraining: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <line
          x1="1"
          y1="1"
          x2="23"
          y2="23"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    ),
  };

  return <span className="trust-icon">{icons[name]}</span>;
}

function FeatureIcon({ name }: { name: (typeof FEATURE_KEYS)[number] }) {
  const icons = {
    widget: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    qualification: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M22 11.08V12a10 10 0 1 1-5.93-9.14"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <polyline
          points="22 4 12 14.01 9 11.01"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    email: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <polyline
          points="22,6 12,13 2,6"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    dashboard: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect
          x="3"
          y="3"
          width="7"
          height="9"
          rx="1"
          stroke="currentColor"
          strokeWidth="2"
        />
        <rect
          x="14"
          y="3"
          width="7"
          height="5"
          rx="1"
          stroke="currentColor"
          strokeWidth="2"
        />
        <rect
          x="14"
          y="12"
          width="7"
          height="9"
          rx="1"
          stroke="currentColor"
          strokeWidth="2"
        />
        <rect
          x="3"
          y="16"
          width="7"
          height="5"
          rx="1"
          stroke="currentColor"
          strokeWidth="2"
        />
      </svg>
    ),
  };

  return <span className="feature-icon">{icons[name]}</span>;
}

export async function LandingPage() {
  const t = await getTranslations("landing");

  return (
    <MarketingShell>
      <section className="landing-section hero shell">
        <div className="hero-copy">
          <p className="eyebrow">{t("eyebrow")}</p>
          <h1 className="landing-hero-title">{t("heroTitle")}</h1>
          <p className="hero-lead">{t("heroLead")}</p>
          <div className="hero-actions">
            <PilotBookingLink className="button button-lg">
              {t("bookPilot")}
            </PilotBookingLink>
            <Link href="#live-demo" className="button secondary button-lg">
              {t("tryDemo")}
            </Link>
          </div>
          <p className="hero-trust-note">{t("heroTrustNote")}</p>
        </div>
        <HeroWebsiteChatPreview />
      </section>

      <section
        className="landing-section landing-section-compact shell"
        aria-label={t("trustTitle")}
      >
        <h2 className="landing-section-title landing-section-title-center">
          {t("trustTitle")}
        </h2>
        <ul className="trust-grid">
          {TRUST_KEYS.map((key) => (
            <li key={key} className="trust-item">
              <TrustIcon name={key} />
              <span>{t(TRUST_I18N_KEYS[key])}</span>
            </li>
          ))}
        </ul>
      </section>

      <LandingComparison />

      <LandingHowItWorks />

      <LandingIndustries />

      <section className="landing-section landing-section-alt shell">
        <header className="landing-section-header">
          <h2 className="landing-section-title">{t("featuresTitle")}</h2>
          <p className="landing-section-lead muted">{t("featuresLead")}</p>
        </header>
        <div className="feature-grid">
          {FEATURE_KEYS.map((key) => (
            <article key={key} className="feature-card card">
              <FeatureIcon name={key} />
              <h3>{t(`features.${key}Title`)}</h3>
              <p className="muted">{t(`features.${key}Description`)}</p>
            </article>
          ))}
        </div>
      </section>

      <LandingSocialProof />

      <LandingPublicDemo />

      <section className="landing-section landing-cta shell">
        <div className="cta-card card">
          <h2 className="landing-section-title">{t("ctaTitle")}</h2>
          <p className="cta-description">{t("ctaDescription")}</p>
          <div className="cta-actions">
            <PilotBookingLink className="button button-lg">
              {t("createPilotAccount")}
            </PilotBookingLink>
            <p className="cta-footnote muted">{t("ctaFootnote")}</p>
          </div>
        </div>
      </section>
    </MarketingShell>
  );
}
