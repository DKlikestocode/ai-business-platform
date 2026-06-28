import { getTranslations } from "next-intl/server";

export async function LandingSocialProof() {
  const t = await getTranslations("landing.socialProof");

  return (
    <section
      className="landing-section landing-section-compact shell"
      aria-labelledby="landing-social-proof-title"
    >
      <header className="landing-section-header landing-section-header-center">
        <h2 id="landing-social-proof-title" className="landing-section-title">
          {t("title")}
        </h2>
      </header>
      <figure className="landing-social-proof-card card">
        <blockquote className="landing-social-proof-quote">
          <p>{t("quote")}</p>
        </blockquote>
        <figcaption className="landing-social-proof-meta">
          <strong>{t("attribution")}</strong>
          <span className="muted">
            {t("role")} · {t("context")}
          </span>
        </figcaption>
      </figure>
    </section>
  );
}
