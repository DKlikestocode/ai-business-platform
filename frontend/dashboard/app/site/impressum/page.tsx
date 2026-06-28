import type { Metadata } from "next";

import { BusinessSiteLegalPage } from "@/components/business-site/business-site-legal-page";
import { fetchPublicBusinessSite } from "@/lib/business-site-api";
import { getBusinessSiteLegalCopy } from "@/lib/business-site-legal-copy";
import { getSiteCompanySlug } from "@/lib/site-config";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  const site = await fetchPublicBusinessSite(getSiteCompanySlug());
  const legal = getBusinessSiteLegalCopy("de", "impressum", site);
  return {
    title: `${legal.title} | ${site.company_name}`,
    description: legal.intro,
  };
}

export default async function SiteImpressumPage() {
  const site = await fetchPublicBusinessSite(getSiteCompanySlug());
  return <BusinessSiteLegalPage site={site} variant="impressum" />;
}
