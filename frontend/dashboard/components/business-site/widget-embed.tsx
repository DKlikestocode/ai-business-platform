"use client";

import Script from "next/script";

import type { PublicBusinessSite } from "@/lib/business-site";

interface BusinessSiteWidgetEmbedProps {
  site: Pick<
    PublicBusinessSite,
    | "widget_company_slug"
    | "widget_api_base"
    | "widget_install_token"
  >;
  privacyUrl?: string;
  welcomeMessage: string;
  requirementsTitle: string;
  requirementsList: string;
}

export function BusinessSiteWidgetEmbed({
  site,
  privacyUrl,
  welcomeMessage,
  requirementsTitle,
  requirementsList,
}: BusinessSiteWidgetEmbedProps) {
  const scriptSrc = `${site.widget_api_base.replace(/\/$/, "")}/static/widget/widget.js?v=8`;

  return (
    <>
      <div
        id="ai-agent-widget"
        data-ai-agent-widget="true"
        data-company-slug={site.widget_company_slug}
        data-api-base={site.widget_api_base}
        data-install-token={site.widget_install_token}
        data-embed-mode="panel"
        data-title="Anfrage senden"
        data-welcome-message={welcomeMessage}
        data-requirements-title={requirementsTitle}
        data-requirements-list={requirementsList}
        {...(privacyUrl ? { "data-privacy-url": privacyUrl } : {})}
      />
      <Script src={scriptSrc} strategy="afterInteractive" />
    </>
  );
}
