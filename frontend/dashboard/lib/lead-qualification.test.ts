import { describe, expect, it } from "vitest";

import {
  LEAD_SORT_OPTIONS,
  QUALIFICATION_STATUSES,
  contactableBadgeClass,
  formatLeadScore,
  isKnownContactMethod,
} from "@/lib/lead-qualification";

describe("lead qualification display helpers", () => {
  it("identifies known contact methods", () => {
    expect(isKnownContactMethod("phone")).toBe(true);
    expect(isKnownContactMethod("email")).toBe(true);
    expect(isKnownContactMethod(null)).toBe(false);
  });

  it("formats lead score as a string", () => {
    expect(formatLeadScore(75)).toBe("75");
  });

  it("uses distinct badge classes for contactable state", () => {
    expect(contactableBadgeClass(true)).toBe("badge-contactable-yes");
    expect(contactableBadgeClass(false)).toBe("badge-contactable-no");
  });

  it("defines qualification statuses for filters", () => {
    expect(QUALIFICATION_STATUSES).toEqual([
      "incomplete",
      "contactable",
      "qualified",
    ]);
  });

  it("defines lead sort options", () => {
    expect(LEAD_SORT_OPTIONS).toEqual([
      "urgency_desc",
      "created_at_desc",
    ]);
  });
});
