import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import {
  formatInquiryNotificationTimestamp,
  getInquiryNotificationStatus,
  isInquiryNotificationSent,
} from "@/lib/inquiry-notification";

describe("isInquiryNotificationSent", () => {
  it("returns true when notification_sent_at is set", () => {
    expect(isInquiryNotificationSent("2026-06-21T10:30:00Z")).toBe(true);
  });

  it("returns false when notification_sent_at is missing", () => {
    expect(isInquiryNotificationSent(null)).toBe(false);
    expect(isInquiryNotificationSent("")).toBe(false);
  });
});

describe("getInquiryNotificationStatus", () => {
  it("maps notification_sent_at to sent", () => {
    expect(getInquiryNotificationStatus("2026-06-21T10:30:00Z")).toBe("sent");
  });

  it("maps missing notification_sent_at to not_sent", () => {
    expect(getInquiryNotificationStatus(null)).toBe("not_sent");
  });
});

describe("formatInquiryNotificationTimestamp", () => {
  it("formats a sent timestamp for owner-facing display", () => {
    const formatted = formatInquiryNotificationTimestamp(
      "2026-06-21T10:30:00Z",
      "de-DE",
      "medium",
    );
    expect(formatted).toBeTruthy();
  });

  it("returns null when notification was not sent", () => {
    expect(formatInquiryNotificationTimestamp(null, "de-DE")).toBeNull();
  });
});

describe("inquiry notification German copy", () => {
  it("uses E-Mail gesendet for card sent state", () => {
    expect(de.leads.notificationSentShort).toBe("E-Mail gesendet");
  });

  it("uses Nicht per E-Mail benachrichtigt for card not sent state", () => {
    expect(de.leads.notificationNotSentShort).toBe(
      "Nicht per E-Mail benachrichtigt",
    );
  });

  it("uses detail copy for sent and not sent states", () => {
    expect(de.leadDetail.notificationSentDetail).toContain("gesendet");
    expect(de.leadDetail.notificationNotSentDetail).toContain(
      "Noch keine E-Mail-Benachrichtigung gesendet",
    );
  });
});
