import { BusinessSiteWidgetEmbed } from "@/components/business-site/widget-embed";
import { getBusinessSiteCopy } from "@/lib/business-site-copy";
import {
  formatBusinessSiteServiceArea,
  getBusinessSiteTradeProfile,
  normalizePhoneHref,
  type PublicBusinessSite,
} from "@/lib/business-site";
import { getBusinessSitePublicBasePath } from "@/lib/site-config";

interface BusinessSitePageProps {
  site: PublicBusinessSite;
}

export function BusinessSitePage({ site }: BusinessSitePageProps) {
  const copy = getBusinessSiteCopy("de");
  const profile = getBusinessSiteTradeProfile(site.trade);
  const serviceArea = formatBusinessSiteServiceArea(
    site.service_area_center,
    site.service_radius_km,
  );
  const phone = site.phone?.trim() ?? "";
  const basePath = getBusinessSitePublicBasePath();

  return (
    <div className="business-site">
      <header className="business-site-header">
        <div className="business-site-container business-site-header-inner">
          <div className="business-site-brand">
            <strong>{site.company_name}</strong>
            <span>{profile.titleSuffix}</span>
          </div>
          <div className="business-site-header-actions">
            {phone ? (
              <a
                className="business-site-header-phone"
                href={`tel:${normalizePhoneHref(phone)}`}
              >
                {phone}
              </a>
            ) : null}
            <a className="button business-site-cta" href="#kontakt">
              {copy.requestCta}
            </a>
          </div>
        </div>
      </header>

      <main>
        <section className="business-site-hero">
          <div className="business-site-container business-site-hero-grid">
            <div className="business-site-hero-card">
              <span className="business-site-eyebrow">{profile.heroKicker}</span>
              <h1 className="business-site-title">{site.company_name}</h1>
              <p className="business-site-lead">{profile.heroSubline}</p>
              <div className="business-site-hero-actions">
                <a className="button business-site-cta" href="#kontakt">
                  {copy.heroPrimaryCta}
                </a>
                <a
                  className="button secondary business-site-cta-secondary"
                  href="#leistungen"
                >
                  {copy.heroSecondaryCta}
                </a>
              </div>
            </div>
            <aside
              className="business-site-hero-panel"
              aria-label={copy.benefitsTitle}
            >
              <h2>{copy.benefitsTitle}</h2>
              <ul className="business-site-checklist">
                {profile.benefits.map((benefit) => (
                  <li key={benefit}>{benefit}</li>
                ))}
              </ul>
            </aside>
          </div>
        </section>

        <section className="business-site-section" id="leistungen">
          <div className="business-site-container">
            <div className="business-site-section-header">
              <h2>{copy.servicesTitle}</h2>
              <p className="muted">{copy.servicesLead}</p>
            </div>
            <div className="business-site-services-grid">
              {profile.services.map((service) => (
                <article key={service.title} className="business-site-service-card">
                  <h3>{service.title}</h3>
                  <p>{service.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="business-site-section">
          <div className="business-site-container business-site-trust-strip">
            <div className="business-site-trust-item">
              <strong>{copy.trustFastTitle}</strong>
              <span>{copy.trustFastBody}</span>
            </div>
            <div className="business-site-trust-item">
              <strong>{copy.trustFairTitle}</strong>
              <span>{copy.trustFairBody}</span>
            </div>
            <div className="business-site-trust-item">
              <strong>{copy.trustRegionalTitle}</strong>
              <span>{serviceArea ?? copy.trustRegionalFallback}</span>
            </div>
          </div>
        </section>

        <section className="business-site-section" id="kontakt">
          <div className="business-site-container">
            <div className="business-site-section-header">
              <h2>{copy.contactTitle}</h2>
              <p className="muted">{copy.contactLead}</p>
            </div>
            <div className="business-site-contact-card">
              <p>
                <strong>{copy.emailLabel}:</strong>{" "}
                <a href={`mailto:${site.email}`}>{site.email}</a>
              </p>
              {phone ? (
                <p>
                  <strong>{copy.phoneLabel}:</strong>{" "}
                  <a href={`tel:${normalizePhoneHref(phone)}`}>{phone}</a>
                </p>
              ) : null}
              {serviceArea ? (
                <p className="business-site-service-area">{serviceArea}</p>
              ) : null}
              <p className="muted">{copy.contactChatHint}</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="business-site-footer">
        <div className="business-site-container business-site-footer-inner">
          <div>
            <strong>{site.company_name}</strong>
            <p>{profile.titleSuffix}</p>
          </div>
          <div>
            <p>
              {copy.emailLabel}: <a href={`mailto:${site.email}`}>{site.email}</a>
            </p>
            {phone ? (
              <p>
                {copy.phoneLabel}:{" "}
                <a href={`tel:${normalizePhoneHref(phone)}`}>{phone}</a>
              </p>
            ) : null}
            <nav
              className="business-site-footer-legal"
              aria-label={copy.legalNavLabel}
            >
              <a href={`${basePath}/impressum`}>{copy.impressumLink}</a>
              <a href={`${basePath}/datenschutz`}>{copy.datenschutzLink}</a>
            </nav>
            <p>© {site.company_name}</p>
          </div>
        </div>
      </footer>

      <BusinessSiteWidgetEmbed site={site} />
    </div>
  );
}
