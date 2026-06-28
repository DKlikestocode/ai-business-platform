import { getTranslations } from "next-intl/server";

const WITHOUT_KEYS = ["item1", "item2", "item3", "item4"] as const;
const WITH_KEYS = ["item1", "item2", "item3", "item4"] as const;

export async function LandingComparison() {
  const t = await getTranslations("landing.comparison");

  return (
    <section
      className="landing-section shell"
      aria-labelledby="landing-comparison-title"
    >
      <header className="landing-section-header landing-section-header-center">
        <h2 id="landing-comparison-title" className="landing-section-title">
          {t("title")}
        </h2>
        <p className="landing-section-lead muted">{t("lead")}</p>
      </header>
      <div className="landing-comparison-grid">
        <article className="landing-comparison-card card landing-comparison-card-muted">
          <h3>{t("withoutTitle")}</h3>
          <ul className="landing-comparison-list">
            {WITHOUT_KEYS.map((key) => (
              <li key={key}>{t(`without.${key}`)}</li>
            ))}
          </ul>
        </article>
        <article className="landing-comparison-card card landing-comparison-card-highlight">
          <h3>{t("withTitle")}</h3>
          <ul className="landing-comparison-list">
            {WITH_KEYS.map((key) => (
              <li key={key}>{t(`with.${key}`)}</li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  );
}
