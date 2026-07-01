"use client";

import { openBusinessSiteChat } from "@/components/business-site/business-site-chat-launcher";

interface BusinessSiteHeaderProps {
  companyName: string;
  titleSuffix: string;
  phone: string | null;
  phoneHref: string | null;
  servicesNavLabel: string;
  contactNavLabel: string;
  chatNavLabel: string;
  requestCta: string;
}

export function BusinessSiteHeader({
  companyName,
  titleSuffix,
  phone,
  phoneHref,
  servicesNavLabel,
  contactNavLabel,
  chatNavLabel,
  requestCta,
}: BusinessSiteHeaderProps) {
  return (
    <header className="business-site-header">
      <div className="business-site-container business-site-header-inner">
        <div className="business-site-brand">
          <strong>{companyName}</strong>
          <span>{titleSuffix}</span>
        </div>

        <nav className="business-site-nav" aria-label="Hauptnavigation">
          <a className="business-site-nav-link" href="#leistungen">
            {servicesNavLabel}
          </a>
          <a className="business-site-nav-link" href="#kontakt">
            {contactNavLabel}
          </a>
          <button
            type="button"
            className="business-site-nav-link business-site-nav-chat"
            onClick={openBusinessSiteChat}
          >
            {chatNavLabel}
          </button>
        </nav>

        <div className="business-site-header-actions">
          {phone && phoneHref ? (
            <a className="business-site-header-phone" href={phoneHref}>
              {phone}
            </a>
          ) : null}
          <button
            type="button"
            className="button business-site-cta"
            onClick={openBusinessSiteChat}
          >
            {requestCta}
          </button>
        </div>
      </div>
    </header>
  );
}
