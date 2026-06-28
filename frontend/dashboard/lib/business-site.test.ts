import { describe, expect, it } from "vitest";

import {
  formatBusinessSiteServiceArea,
  getBusinessSiteTradeProfile,
} from "@/lib/business-site";

describe("business-site", () => {
  it("returns skh profile for skh trade", () => {
    const profile = getBusinessSiteTradeProfile("skh");
    expect(profile.titleSuffix).toContain("Sanitär");
    expect(profile.services).toHaveLength(4);
  });

  it("formats service area with radius", () => {
    expect(formatBusinessSiteServiceArea("22303 Hamburg", 30)).toBe(
      "22303 Hamburg und Umgebung (ca. 30 km)",
    );
  });
});
