import { describe, expect, it } from "vitest";

import {
  CONTACT_METHOD_LABELS,
  QUALIFICATION_LABELS,
  contactableBadgeClass,
  formatContactMethod,
  formatContactable,
  formatLeadScore,
} from "@/lib/lead-qualification";

describe("lead qualification display helpers", () => {
  it("formats contactable as yes/no", () => {
    expect(formatContactable(true)).toBe("Yes");
    expect(formatContactable(false)).toBe("No");
  });

  it("maps contact methods to labels", () => {
    expect(formatContactMethod("phone")).toBe(CONTACT_METHOD_LABELS.phone);
    expect(formatContactMethod("email")).toBe(CONTACT_METHOD_LABELS.email);
    expect(formatContactMethod(null)).toBe("—");
  });

  it("formats lead score as a string", () => {
    expect(formatLeadScore(75)).toBe("75");
  });

  it("uses distinct badge classes for contactable state", () => {
    expect(contactableBadgeClass(true)).toBe("badge-contactable-yes");
    expect(contactableBadgeClass(false)).toBe("badge-contactable-no");
  });

  it("defines qualification labels for all statuses", () => {
    expect(QUALIFICATION_LABELS.incomplete).toBe("Incomplete");
    expect(QUALIFICATION_LABELS.contactable).toBe("Contactable");
    expect(QUALIFICATION_LABELS.qualified).toBe("Qualified");
  });
});
