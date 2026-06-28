import { describe, expect, it } from "vitest";

import {
  getConfiguredSiteHostnames,
  isBusinessSiteHostname,
  parseSiteHostnames,
} from "@/lib/site-config";

describe("site-config", () => {
  it("parses comma-separated hostnames", () => {
    expect(parseSiteHostnames("example.com, www.example.com")).toEqual([
      "example.com",
      "www.example.com",
    ]);
  });

  it("detects configured business site hosts", () => {
    const hosts = ["dominiksdomain.com", "www.dominiksdomain.com"];
    expect(isBusinessSiteHostname("dominiksdomain.com", hosts)).toBe(true);
    expect(isBusinessSiteHostname("www.dominiksdomain.com:443", hosts)).toBe(
      true,
    );
    expect(isBusinessSiteHostname("app.dominiksdomain.com", hosts)).toBe(false);
  });

  it("returns empty hostnames when unset", () => {
    expect(getConfiguredSiteHostnames()).toEqual([]);
  });
});
