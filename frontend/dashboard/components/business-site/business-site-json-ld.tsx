import { buildBusinessSiteJsonLd } from "@/lib/business-site-seo";
import type { PublicBusinessSite } from "@/lib/business-site";

interface BusinessSiteJsonLdProps {
  site: PublicBusinessSite;
  siteUrl: string;
}

export function BusinessSiteJsonLd({ site, siteUrl }: BusinessSiteJsonLdProps) {
  const jsonLd = buildBusinessSiteJsonLd(site, siteUrl);

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}
