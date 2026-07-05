import Image from "next/image";

import { BusinessSiteChatLauncher } from "@/components/business-site/business-site-chat-launcher";
import { BusinessSiteHeader } from "@/components/business-site/business-site-header";
import { BusinessSiteJsonLd } from "@/components/business-site/business-site-json-ld";
import { BusinessSiteOpenChatButton } from "@/components/business-site/business-site-open-chat-button";
import { BusinessSiteWidgetEmbed } from "@/components/business-site/widget-embed";
import { getBusinessSiteCopy } from "@/lib/business-site-copy";
import {
  formatBusinessSiteServiceArea,
  getBusinessSiteContactEmail,
  getBusinessSiteProfile,
  normalizePhoneHref,
  type PublicBusinessSite,
} from "@/lib/business-site";
import {
  getBusinessSitePublicBasePath,
  getBusinessSitePublicOrigin,
} from "@/lib/site-config";

interface BusinessSitePageProps {
  site: PublicBusinessSite;
}

export function BusinessSitePage({ site }: BusinessSitePageProps) {
  const copy = getBusinessSiteCopy("de");
  const profile = getBusinessSiteProfile(site);
  const serviceArea = formatBusinessSiteServiceArea(
    site.service_area_center,
    site.service_radius_km,
  );
  const phone = site.phone?.trim() ?? "";
  const phoneHref = phone ? `tel:${normalizePhoneHref(phone)}` : null;
  const contactEmail = getBusinessSiteContactEmail(site);
  const basePath = getBusinessSitePublicBasePath();
  const siteUrl = getBusinessSitePublicOrigin();
  const privacyUrl = `${siteUrl}${basePath}/datenschutz`;

  return (
    <div className="business-site">
      <BusinessSiteJsonLd site={site} siteUrl={siteUrl} />

      <BusinessSiteHeader
        companyName={site.company_name}
        titleSuffix={profile.titleSuffix}
        phone={phone || null}
        phoneHref={phoneHref}
        servicesNavLabel={copy.navServices}
        contactNavLabel={copy.navContact}
        chatNavLabel={copy.navChat}
        requestCta={copy.requestCta}
      />

      <main>
        <section className="business-site-hero business-site-hero-media">
          <Image
            src="/business-site/hero.jpg"
            alt=""
            fill
            priority
            sizes="100vw"
            className="business-site-hero-image"
          />
          <div className="business-site-hero-overlay" aria-hidden="true" />
          <div className="business-site-container business-site-hero-shell">
            <div className="business-site-hero-content">
              <span className="business-site-eyebrow">{profile.heroKicker}</span>
              <h1 className="business-site-title">{site.company_name}</h1>
              <p className="business-site-lead">{profile.heroSubline}</p>
              <div className="business-site-badges" aria-label={copy.badgesLabel}>
                {copy.badges.map((badge) => (
                  <span key={badge} className="business-site-badge">
                    {badge}
                  </span>
                ))}
              </div>
              <div className="business-site-hero-actions">
                <BusinessSiteOpenChatButton className="button business-site-cta">
                  {copy.heroPrimaryCta}
                </BusinessSiteOpenChatButton>
                {phoneHref ? (
                  <a className="button secondary business-site-cta-secondary" href={phoneHref}>
                    {phone}
                  </a>
                ) : (
                  <a
                    className="button secondary business-site-cta-secondary"
                    href="#leistungen"
                  >
                    {copy.heroSecondaryCta}
                  </a>
                )}
              </div>
            </div>
            <aside
              className="business-site-hero-panel business-site-hero-panel-floating"
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

        {profile.references && profile.references.length > 0 ? (
          <section className="business-site-section business-site-section-alt">
            <div className="business-site-container">
              <div className="business-site-section-header">
                <h2>{copy.referencesTitle}</h2>
                <p className="muted">{copy.referencesLead}</p>
              </div>
              <div className="business-site-references-grid">
                {profile.references.map((item) => (
                  <article
                    key={item.title}
                    className="business-site-reference-card"
                  >
                    <h3>{item.title}</h3>
                    <p>{item.description}</p>
                  </article>
                ))}
              </div>
            </div>
          </section>
        ) : null}

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
            <div className="business-site-contact-grid">
              <div className="business-site-contact-card">
                <p>
                  <strong>{copy.emailLabel}:</strong>{" "}
                  <a href={`mailto:${contactEmail}`}>{contactEmail}</a>
                </p>
                {phone ? (
                  <p>
                    <strong>{copy.phoneLabel}:</strong>{" "}
                    <a href={phoneHref!}>{phone}</a>
                  </p>
                ) : null}
                {serviceArea ? (
                  <p className="business-site-service-area">{serviceArea}</p>
                ) : null}
                <p className="muted">{copy.hoursLabel}</p>
                <p className="muted">{copy.contactChatHint}</p>
              </div>
              <div className="business-site-chat-teaser card" id="anfrage">
                <p className="business-site-eyebrow">{copy.chatTeaserEyebrow}</p>
                <h3>{copy.chatTeaserTitle}</h3>
                <p className="muted">{copy.chatTeaserBody}</p>
                <BusinessSiteOpenChatButton className="button business-site-cta">
                  {copy.chatTeaserCta}
                </BusinessSiteOpenChatButton>
              </div>
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
              {copy.emailLabel}: <a href={`mailto:${contactEmail}`}>{contactEmail}</a>
            </p>
            {phone ? (
              <p>
                {copy.phoneLabel}: <a href={phoneHref!}>{phone}</a>
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

      <BusinessSiteChatLauncher
        title={copy.chatPanelTitle}
        subtitle={copy.chatPanelSubtitle}
        closeLabel={copy.chatCloseLabel}
        restartLabel={copy.chatRestartLabel}
        launcherLabel={copy.chatLauncherLabel}
      >
        <BusinessSiteWidgetEmbed
          site={site}
          privacyUrl={privacyUrl}
          welcomeMessage={copy.chatWelcomeMessage}
          requirementsTitle={copy.chatRequirementsTitle}
          requirementsList={copy.chatRequirementsList}
        />
      </BusinessSiteChatLauncher>
    </div>
  );
}
