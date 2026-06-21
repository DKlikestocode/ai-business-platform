import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import en from "@/messages/en.json";
import {
  canSendTestNotification,
  isNotificationEmailDirty,
} from "@/lib/notification-settings";

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
    expect(
      canSendTestNotification("alerts@acme.co", "ops@acme.co"),
    ).toBe(false);
    expect(canSendTestNotification(null, "ops@acme.co")).toBe(false);
  });

  it("allows test send when saved email matches draft", () => {
    expect(
      canSendTestNotification("alerts@acme.co", "alerts@acme.co"),
    ).toBe(true);
    expect(
      canSendTestNotification(" alerts@acme.co ", "alerts@acme.co"),
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
