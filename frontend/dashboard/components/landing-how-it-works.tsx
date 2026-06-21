import { getTranslations } from "next-intl/server";

const HOW_IT_WORKS_STEP_KEYS = ["start", "embed", "inquiries"] as const;

export async function LandingHowItWorks() {
  const t = await getTranslations("landing.howItWorks");

  return (
    <section
      className="landing-section landing-section-alt how-it-works shell"
      aria-labelledby="how-it-works-title"
    >
      <header className="landing-section-header landing-section-header-center">
        <h2 id="how-it-works-title" className="landing-section-title">
          {t("title")}
        </h2>
        <p className="landing-section-lead muted">{t("lead")}</p>
      </header>
      <ol className="how-it-works-steps">
        {HOW_IT_WORKS_STEP_KEYS.map((key, index) => (
          <li key={key} className="how-it-works-step card">
            <span className="how-it-works-index" aria-hidden="true">
              {index + 1}
            </span>
            <div className="how-it-works-step-body">
              <h3>{t(`steps.${key}.title`)}</h3>
              <p className="muted">{t(`steps.${key}.description`)}</p>
              <p className="how-it-works-outcome">{t(`steps.${key}.outcome`)}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
