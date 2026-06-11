import { getTranslations } from "next-intl/server";

const PREVIEW_MESSAGE_KEYS = [
  "customer1",
  "assistant1",
  "customer2",
] as const;

const PREVIEW_SERVICE_KEYS = ["service1", "service2", "service3"] as const;
const PREVIEW_NAV_KEYS = ["nav1", "nav2", "nav3"] as const;

export async function HeroWebsiteChatPreview() {
  const t = await getTranslations("landing.preview");
  const companyName = t("companyName");
  const customerLabel = t("customerLabel");

  return (
    <div className="hero-preview" role="img" aria-label={t("ariaLabel")}>
      <div className="hero-preview-scene">
        <div className="hero-preview-site">
          <header className="hero-preview-site-header">
            <div className="hero-preview-brand">
              <span className="hero-preview-brand-mark" aria-hidden="true">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              <span className="hero-preview-brand-name">{companyName}</span>
            </div>
            <nav className="hero-preview-site-nav" aria-hidden="true">
              {PREVIEW_NAV_KEYS.map((key) => (
                <span key={key} className="hero-preview-site-nav-item">
                  {t(key)}
                </span>
              ))}
            </nav>
          </header>

          <div className="hero-preview-site-hero">
            <h2 className="hero-preview-site-headline">{t("siteHeadline")}</h2>
            <p className="hero-preview-site-subline">{t("siteSubline")}</p>
            <span className="hero-preview-site-cta">{t("siteCta")}</span>
          </div>

          <ul className="hero-preview-site-services" aria-hidden="true">
            {PREVIEW_SERVICE_KEYS.map((key) => (
              <li key={key}>{t(key)}</li>
            ))}
          </ul>
        </div>

        <div className="hero-preview-widget">
          <div className="hero-preview-widget-header">{companyName}</div>
          <div className="hero-preview-widget-messages">
            {PREVIEW_MESSAGE_KEYS.map((key, index) => {
              const isCustomer = index % 2 === 0;
              const role = isCustomer ? "customer" : "assistant";

              return (
                <div
                  key={key}
                  className={`hero-preview-message hero-preview-message-${role}`}
                >
                  <span className="hero-preview-message-label">
                    {isCustomer ? customerLabel : companyName}
                  </span>
                  <p>{t(key)}</p>
                </div>
              );
            })}
          </div>
          <p className="hero-preview-widget-privacy">{t("privacyHint")}</p>
          <div className="hero-preview-widget-form" aria-hidden="true">
            <span className="hero-preview-widget-input">{t("inputPlaceholder")}</span>
            <span className="hero-preview-widget-send">{t("sendLabel")}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
