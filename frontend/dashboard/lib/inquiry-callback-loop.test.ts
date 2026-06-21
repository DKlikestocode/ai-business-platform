import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import {
  getPrimaryContactAction,
  shouldPromptMarkContacted,
  shouldShowMarkContactedAction,
} from "@/lib/inquiry-callback-loop";

describe("getPrimaryContactAction", () => {
  it("prefers phone when phone exists", () => {
    expect(getPrimaryContactAction("+49 170 1234567", "info@example.com")).toBe(
      "phone",
    );
  });

  it("uses email when only email exists", () => {
    expect(getPrimaryContactAction(null, "info@example.com")).toBe("email");
  });

  it("returns none when contact data is missing", () => {
    expect(getPrimaryContactAction(null, null)).toBe("none");
  });
});

describe("shouldShowMarkContactedAction", () => {
  it("shows mark contacted for new inquiries with phone", () => {
    expect(shouldShowMarkContactedAction(true, "new")).toBe(true);
  });

  it("shows mark contacted for new inquiries with email only", () => {
    expect(shouldShowMarkContactedAction(true, "new")).toBe(true);
  });

  it("hides mark contacted when status is already contacted", () => {
    expect(shouldShowMarkContactedAction(true, "contacted")).toBe(false);
  });

  it("hides mark contacted when contact data is missing", () => {
    expect(shouldShowMarkContactedAction(false, "new")).toBe(false);
  });
});

describe("shouldPromptMarkContacted", () => {
  it("prompts only for new status", () => {
    expect(shouldPromptMarkContacted("new")).toBe(true);
    expect(shouldPromptMarkContacted("contacted")).toBe(false);
    expect(shouldPromptMarkContacted("won")).toBe(false);
  });
});

describe("inquiry callback German copy", () => {
  it("uses owner-facing callback copy", () => {
    expect(de.leadDetail.markContacted).toBe("Als kontaktiert markieren");
    expect(de.leadDetail.markContactedHint).toContain("Kontakt");
    expect(de.leadDetail.markContactedSuccess).toBe("Als kontaktiert markiert");
    expect(de.leadDetail.missingContact).toBe("Kontaktdaten fehlen");
  });
});
