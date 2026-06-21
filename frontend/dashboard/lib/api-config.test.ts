import { describe, expect, it } from "vitest";

import { buildV1ApiUrl } from "@/lib/api-config";

describe("buildV1ApiUrl", () => {
  it("prefixes public paths for the next.js api rewrite", () => {
    expect(buildV1ApiUrl("/public/landing-demo/message")).toMatch(
      /\/api\/v1\/public\/landing-demo\/message$/,
    );
  });

  it("leaves fully qualified v1 paths unchanged", () => {
    expect(buildV1ApiUrl("/api/v1/leads")).toMatch(/\/api\/v1\/leads$/);
  });
});
