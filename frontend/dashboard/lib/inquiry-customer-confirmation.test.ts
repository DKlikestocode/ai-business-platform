import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import {
  formatCustomerConfirmationTimestamp,
  getCustomerConfirmationStatus,
  isCustomerConfirmationSent,
  shouldShowCustomerConfirmationIndicator,
} from "@/lib/inquiry-customer-confirmation";

describe("isCustomerConfirmationSent", () => {
  it("returns true when customer_confirmation_sent_at is set", () => {
    expect(isCustomerConfirmationSent("2026-06-21T10:30:00Z")).toBe(true);
  });

  it("returns false when customer_confirmation_sent_at is missing", () => {
    expect(isCustomerConfirmationSent(null)).toBe(false);
    expect(isCustomerConfirmationSent("")).toBe(false);
  });
});

describe("getCustomerConfirmationStatus", () => {
  it("maps customer_confirmation_sent_at to sent", () => {
    expect(getCustomerConfirmationStatus("2026-06-21T10:30:00Z")).toBe("sent");
  });

  it("maps missing customer_confirmation_sent_at to not_sent", () => {
    expect(getCustomerConfirmationStatus(null)).toBe("not_sent");
  });
});

describe("formatCustomerConfirmationTimestamp", () => {
  it("formats a sent timestamp for owner-facing display", () => {
    const formatted = formatCustomerConfirmationTimestamp(
      "2026-06-21T10:30:00Z",
      "de-DE",
      "medium",
    );
    expect(formatted).toBeTruthy();
  });

  it("returns null when confirmation was not sent", () => {
    expect(formatCustomerConfirmationTimestamp(null, "de-DE")).toBeNull();
  });
});

describe("shouldShowCustomerConfirmationIndicator", () => {
  it("shows when send_customer_confirmation is enabled", () => {
    expect(shouldShowCustomerConfirmationIndicator(true, null)).toBe(true);
  });

  it("shows when confirmation was sent even if setting is off", () => {
    expect(
      shouldShowCustomerConfirmationIndicator(false, "2026-06-21T10:30:00Z"),
    ).toBe(true);
  });

  it("hides when setting is off and confirmation was not sent", () => {
    expect(shouldShowCustomerConfirmationIndicator(false, null)).toBe(false);
  });
});

describe("customer confirmation German copy", () => {
  it("uses Kundenbestätigung gesendet for card sent state", () => {
    expect(de.leads.customerConfirmationSentShort).toBe(
      "Kundenbestätigung gesendet",
    );
  });

  it("uses soft pending copy for card not sent state", () => {
    expect(de.leads.customerConfirmationNotSentShort).toBe(
      "Kundenbestätigung ausstehend",
    );
  });

  it("uses detail copy for sent and not sent states", () => {
    expect(de.leadDetail.customerConfirmationSentDetail).toContain("gesendet");
    expect(de.leadDetail.customerConfirmationNotSentDetail).toContain(
      "Noch keine Kundenbestätigung gesendet",
    );
  });
});
