import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import en from "@/messages/en.json";
import {
  areNotificationRecipientSettingsDirty,
  canSendTestNotification,
  isNotificationEmailDirty,
} from "@/lib/notification-settings";
import type { CompanySettings } from "@/lib/types";

const baseSettings: CompanySettings = {
  name: "Acme",
  slug: "acme",
  email: "office@acme.co",
  phone: null,
  notification_email: "alerts@acme.co",
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

describe("notification settings helpers", () => {
  it("treats matching saved and draft emails as clean", () => {
    expect(isNotificationEmailDirty("alerts@acme.co", "alerts@acme.co")).toBe(
      false,
    );
    expect(isNotificationEmailDirty(" alerts@acme.co ", "alerts@acme.co")).toBe(
      false,
    );
    expect(isNotificationEmailDirty(null, "")).toBe(false);
  });

  it("treats unsaved draft changes as dirty", () => {
    expect(
      isNotificationEmailDirty("alerts@acme.co", "ops@acme.co"),
    ).toBe(true);
    expect(isNotificationEmailDirty(null, "ops@acme.co")).toBe(true);
    expect(isNotificationEmailDirty("alerts@acme.co", "")).toBe(true);
  });

  it("disables test send when notification settings are unsaved", () => {
    expect(
      canSendTestNotification(baseSettings, {
        ...baseSettings,
        notification_email: "ops@acme.co",
      }),
    ).toBe(false);
    expect(
      canSendTestNotification(
        { ...baseSettings, notification_email: null },
        { ...baseSettings, notification_email: null, email: "ops@acme.co" },
      ),
    ).toBe(false);
  });

  it("allows test send when saved recipient matches draft", () => {
    expect(canSendTestNotification(baseSettings, baseSettings)).toBe(true);
    expect(
      canSendTestNotification(
        { ...baseSettings, notification_email: null },
        { ...baseSettings, notification_email: null },
      ),
    ).toBe(true);
  });

  it("detects dirty company email changes", () => {
    expect(
      areNotificationRecipientSettingsDirty(baseSettings, {
        ...baseSettings,
        email: "ops@acme.co",
      }),
    ).toBe(true);
  });

  it("includes save-first copy in DE and EN", () => {
    expect(de.settings.testNotificationSaveFirst).toBe(
      "Bitte speichern Sie die E-Mail-Adresse zuerst.",
    );
    expect(en.settings.testNotificationSaveFirst).toBe(
      "Please save the email address first.",
    );
  });
});
