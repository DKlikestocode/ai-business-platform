import { getTranslations } from "next-intl/server";

const HOW_IT_WORKS_STEP_KEYS = ["start", "embed", "inquiries"] as const;

export async function LandingHowItWorks() {
  const t = await getTranslations("landing.howItWorks");

  return (
    <section
      className="how-it-works shell"
      aria-labelledby="how-it-works-title"
    >
      <h2 id="how-it-works-title" className="how-it-works-title">
        {t("title")}
      </h2>
      <p className="how-it-works-lead muted">{t("lead")}</p>
      <ol className="how-it-works-steps">
        {HOW_IT_WORKS_STEP_KEYS.map((key, index) => (
          <li key={key} className="how-it-works-step card">
            <span className="how-it-works-index" aria-hidden="true">
              {index + 1}
            </span>
            <div>
              <h3>{t(`steps.${key}.title`)}</h3>
              <p className="muted">{t(`steps.${key}.description`)}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
