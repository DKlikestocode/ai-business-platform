import { describe, expect, it } from "vitest";

import { buildBusinessSiteJsonLd, buildBusinessSiteMetadata } from "@/lib/business-site-seo";

const site = {
  company_name: "Dominik's Dienstleistungsbetrieb",
  company_slug: "demo-betrieb",
  email: "hallo@example.com",
  phone: "+49 177 7499676",
  trade: "skh",
  service_area_center: "Hamburg-Wandsbek",
  service_radius_km: 30,
  widget_company_slug: "demo-betrieb",
  widget_api_base: "https://api.example.com",
  widget_install_token: "token",
  widget_title: "Terminanfrage stellen",
};

describe("business-site-seo", () => {
  it("builds metadata with open graph", () => {
    const metadata = buildBusinessSiteMetadata(site, "https://dominiksdomain.com");
    expect(metadata.title).toContain("Dominik");
    expect(metadata.openGraph?.url).toBe("https://dominiksdomain.com");
    expect(metadata.openGraph?.images?.[0]?.url).toBe(
      "https://dominiksdomain.com/business-site/hero.jpg",
    );
  });

  it("builds local business json-ld", () => {
    const jsonLd = buildBusinessSiteJsonLd(site, "https://dominiksdomain.com");
    expect(jsonLd["@type"]).toBe("LocalBusiness");
    expect(jsonLd.telephone).toBe("+49 177 7499676");
  });
});
