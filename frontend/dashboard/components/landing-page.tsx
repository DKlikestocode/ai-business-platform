import { getTranslations } from "next-intl/server";

import { MarketingShell } from "@/components/marketing-shell";
import { Link } from "@/i18n/navigation";

const FEATURE_KEYS = [
  "widget",
  "qualification",
  "email",
  "dashboard",
] as const;

export async function LandingPage() {
  const t = await getTranslations("landing");

  return (
    <MarketingShell>
      <section className="hero shell">
        <div className="hero-copy">
          <p className="eyebrow">{t("eyebrow")}</p>
          <h1>{t("heroTitle")}</h1>
          <p className="hero-lead">{t("heroLead")}</p>
          <div className="hero-actions">
            <Link href="/onboarding" className="button button-lg">
              {t("startPilot")}
            </Link>
            <Link href="/login" className="button secondary button-lg">
              {t("signIn")}
            </Link>
          </div>
        </div>
        <div className="hero-card card">
          <h2>{t("dayOneTitle")}</h2>
          <ul className="hero-list">
            <li>{t("dayOneWidget")}</li>
            <li>{t("dayOneScoring")}</li>
            <li>{t("dayOneDashboard")}</li>
            <li>{t("dayOneEmail")}</li>
          </ul>
        </div>
      </section>

      <section className="trust-band shell" aria-label={t("trustTitle")}>
        <h2 className="trust-band-title">{t("trustTitle")}</h2>
        <ul className="trust-list">
          <li>{t("trustGdpr")}</li>
          <li>{t("trustHttps")}</li>
          <li>{t("trustHosting")}</li>
          <li>{t("trustNoTraining")}</li>
        </ul>
      </section>

      <section className="feature-grid shell">
        {FEATURE_KEYS.map((key) => (
          <article key={key} className="feature-card card">
            <h3>{t(`features.${key}Title`)}</h3>
            <p className="muted">{t(`features.${key}Description`)}</p>
          </article>
        ))}
      </section>

      <section className="cta-band shell">
        <div className="cta-card card">
          <h2>{t("ctaTitle")}</h2>
          <p className="muted">{t("ctaDescription")}</p>
          <Link href="/onboarding" className="button">
            {t("createPilotAccount")}
          </Link>
        </div>
      </section>
    </MarketingShell>
  );
}
