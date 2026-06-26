import { describe, expect, it } from "vitest";

import {
  isNotificationConfigured,
  resolveNotificationRecipient,
} from "@/lib/notification-recipient";
import type { CompanySettings } from "@/lib/types";

const baseSettings: CompanySettings = {
  name: "Acme",
  slug: "acme",
  email: "hello@acme.co",
  phone: null,
  notification_email: null,
  notification_min_urgency: "medium" as const,
  service_area_center: null,
  service_radius_km: null,
  email_delivery_provider: "logging",
  email_delivery_ready: true,
  email_delivery_sends_real_email: false,
  created_at: "2026-06-10T12:00:00Z",
};

describe("notification recipient", () => {
  it("prefers explicit notification email over company email", () => {
    const settings = {
      ...baseSettings,
      notification_email: "alerts@acme.co",
    };

    expect(resolveNotificationRecipient(settings)).toBe("alerts@acme.co");
    expect(isNotificationConfigured(settings)).toBe(true);
  });

  it("falls back to company email when notification email is empty", () => {
    const settings = {
      ...baseSettings,
      notification_email: null,
    };

    expect(resolveNotificationRecipient(settings)).toBe("hello@acme.co");
    expect(isNotificationConfigured(settings)).toBe(true);
  });

  it("returns inactive when both addresses are missing", () => {
    const settings = {
      ...baseSettings,
      email: "",
      notification_email: null,
    };

    expect(resolveNotificationRecipient(settings)).toBe("");
    expect(isNotificationConfigured(settings)).toBe(false);
  });
});
