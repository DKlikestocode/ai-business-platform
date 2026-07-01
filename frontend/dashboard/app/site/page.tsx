import type { Metadata } from "next";

import { BusinessSitePage } from "@/components/business-site/business-site-page";
import { buildBusinessSiteMetadata } from "@/lib/business-site-seo";
import { fetchPublicBusinessSite } from "@/lib/business-site-api";
import { getBusinessSiteCopy } from "@/lib/business-site-copy";
import {
  getBusinessSitePublicOrigin,
  getSiteCompanySlug,
} from "@/lib/site-config";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  try {
    const site = await fetchPublicBusinessSite(getSiteCompanySlug());
    return buildBusinessSiteMetadata(site, getBusinessSitePublicOrigin());
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
