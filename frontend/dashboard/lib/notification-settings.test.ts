import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import en from "@/messages/en.json";
import {
  canSendTestNotification,
  isNotificationEmailDirty,
} from "@/lib/notification-settings";
import type { CompanySettings } from "@/lib/types";

const baseSettings: CompanySettings = {
  name: "Acme",
  slug: "acme",
  email: "hello@acme.co",
  phone: null,
  notification_email: null,
  notification_min_urgency: "medium",
  service_area_center: null,
  service_radius_km: null,
  trade: null,
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

  it("disables test send when notification email is unsaved", () => {
    const saved = { ...baseSettings, notification_email: "alerts@acme.co" };
    const draft = { ...saved, notification_email: "ops@acme.co" };

    expect(canSendTestNotification(saved, draft)).toBe(false);
  });

  it("allows test send when saved email matches draft", () => {
    const saved = { ...baseSettings, notification_email: "alerts@acme.co" };

    expect(canSendTestNotification(saved, saved)).toBe(true);
    expect(
      canSendTestNotification(
        { ...saved, notification_email: " alerts@acme.co " },
        saved,
      ),
    ).toBe(true);
  });

  it("allows test send when company email is the configured fallback", () => {
    const saved = { ...baseSettings, notification_email: null };

    expect(canSendTestNotification(saved, saved)).toBe(true);
  });

  it("includes save-first copy in DE and EN", () => {
    expect(de.settings.testNotificationSaveFirst).toBe(
      "Bitte speichern Sie die E-Mail-Adresse zuerst.",
    );
    expect(en.settings.testNotificationSaveFirst).toBe(
      "Please save the email address first.",
    );
  });

  it("includes urgency notification copy in DE and EN", () => {
    expect(de.settings.notificationMinUrgency).toBe(
      "Benachrichtigen ab Dringlichkeit",
    );
    expect(en.settings.notificationMinUrgencyOptions.medium).toContain(
      "recommended",
    );
  });
});
