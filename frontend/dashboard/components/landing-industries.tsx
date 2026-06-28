import { getTranslations } from "next-intl/server";

const INDUSTRY_KEYS = ["skh", "roof", "electrical"] as const;

export async function LandingIndustries() {
  const t = await getTranslations("landing.industries");

  return (
    <section
      className="landing-section landing-section-alt shell"
      aria-labelledby="landing-industries-title"
    >
      <header className="landing-section-header landing-section-header-center">
        <h2 id="landing-industries-title" className="landing-section-title">
          {t("title")}
        </h2>
        <p className="landing-section-lead muted">{t("lead")}</p>
      </header>
      <div className="landing-industries-grid">
        {INDUSTRY_KEYS.map((key) => (
          <article key={key} className="landing-industry-card card">
            <h3>{t(`items.${key}.title`)}</h3>
            <p className="muted">{t(`items.${key}.description`)}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
