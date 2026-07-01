import type { Metadata } from "next";

import type { PublicBusinessSite } from "@/lib/business-site";
import { getBusinessSiteProfile } from "@/lib/business-site";

export function buildBusinessSiteMetadata(
  site: PublicBusinessSite,
  siteUrl: string,
): Metadata {
  const profile = getBusinessSiteProfile(site);
  const title = `${site.company_name} | ${profile.titleSuffix}`;
  const description = `${site.company_name} in ${site.service_area_center ?? "Ihrer Region"} — ${profile.heroSubline.slice(0, 140)}…`;

  return {
    title,
    description,
    openGraph: {
      type: "website",
      locale: "de_DE",
      url: siteUrl,
      title,
      description,
      siteName: site.company_name,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
    alternates: {
      canonical: siteUrl,
    },
  };
}

export function buildBusinessSiteJsonLd(
  site: PublicBusinessSite,
  siteUrl: string,
): Record<string, unknown> {
  const profile = getBusinessSiteProfile(site);
  const phone = site.phone?.trim();

  return {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    name: site.company_name,
    description: profile.heroSubline,
    url: siteUrl,
    email: site.email,
    ...(phone ? { telephone: phone } : {}),
    ...(site.service_area_center
      ? {
          areaServed: site.service_area_center,
          address: {
            "@type": "PostalAddress",
            addressLocality: site.service_area_center,
            addressCountry: "DE",
          },
        }
      : {}),
  };
}
