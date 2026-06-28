import type { Metadata } from "next";

import { BusinessSitePage } from "@/components/business-site/business-site-page";
import { getBusinessSiteTradeProfile } from "@/lib/business-site";
import { fetchPublicBusinessSite } from "@/lib/business-site-api";
import { getBusinessSiteCopy } from "@/lib/business-site-copy";
import { getSiteCompanySlug } from "@/lib/site-config";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  try {
    const site = await fetchPublicBusinessSite(getSiteCompanySlug());
    const profile = getBusinessSiteTradeProfile(site.trade);
    return {
      title: `${site.company_name} | ${profile.titleSuffix}`,
      description: `${site.company_name} — ${profile.titleSuffix}. Jetzt Anfrage stellen per Chat oder E-Mail.`,
    };
  } catch {
    const copy = getBusinessSiteCopy("de");
    return {
      title: copy.loadFailedTitle,
      description: copy.loadFailedBody,
    };
  }
}

export default async function SiteHomePage() {
  const site = await fetchPublicBusinessSite(getSiteCompanySlug());
  return <BusinessSitePage site={site} />;
}
