import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import en from "@/messages/en.json";
import { INQUIRY_SOURCE_BADGE_CLASS } from "@/lib/inquiry-source";

describe("inquiry source badges", () => {
  it("includes owner-facing German labels", () => {
    expect(de.leads.sourceWebsite).toBe("Website");
    expect(de.leads.sourceTest).toBe("Test");
    expect(de.leads.sourcePhone).toBe("Telefon");
  });

  it("includes English labels", () => {
    expect(en.leads.sourceWebsite).toBe("Website");
    expect(en.leads.sourceTest).toBe("Test");
    expect(en.leads.sourcePhone).toBe("Phone");
  });

  it("maps sources to badge classes", () => {
    expect(INQUIRY_SOURCE_BADGE_CLASS.website).toBe("badge-source-website");
    expect(INQUIRY_SOURCE_BADGE_CLASS.test).toBe("badge-source-test");
    expect(INQUIRY_SOURCE_BADGE_CLASS.phone).toBe("badge-source-phone");
  });
});
