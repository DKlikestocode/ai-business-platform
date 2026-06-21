import { describe, expect, it } from "vitest";

import {
  isNotificationRecipientConfigured,
  resolveNotificationRecipient,
} from "@/lib/notification-recipient";
import type { CompanySettings } from "@/lib/types";

const baseSettings: CompanySettings = {
  name: "Acme",
  slug: "acme",
  email: "office@acme.co",
  phone: null,
  notification_email: null,
  notify_on_new_lead: true,
  notify_on_contactable_lead: true,
  contactable_lead_notification_threshold: 50,
  service_area_center: null,
  service_radius_km: null,
  email_delivery_provider: "logging",
  email_delivery_ready: true,
  email_delivery_sends_real_email: false,
  created_at: "2026-06-10T12:00:00Z",
};

describe("notification recipient", () => {
  it("prefers dedicated notification email", () => {
    expect(
      resolveNotificationRecipient({
        ...baseSettings,
        notification_email: "alerts@acme.co",
      }),
    ).toBe("alerts@acme.co");
  });

  it("falls back to company email", () => {
    expect(resolveNotificationRecipient(baseSettings)).toBe("office@acme.co");
    expect(isNotificationRecipientConfigured(baseSettings)).toBe(true);
  });
});
