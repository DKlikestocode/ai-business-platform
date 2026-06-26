import { describe, expect, it } from "vitest";

import {
  ONBOARDING_STEPS,
  countCompletedSteps,
  evaluateOnboardingProgress,
  isOnboardingComplete,
} from "@/lib/onboarding";
import type { CompanySettings } from "@/lib/types";

const settings: CompanySettings = {
  name: "Acme",
  slug: "acme",
  email: "hello@acme.co",
  phone: null,
  notification_email: "alerts@acme.co",
  notification_min_urgency: "medium" as const,
  service_area_center: null,
  service_radius_km: null,
  email_delivery_provider: "logging",
  email_delivery_ready: true,
  email_delivery_sends_real_email: false,
  created_at: "2026-06-10T12:00:00Z",
};

describe("onboarding progress", () => {
  it("marks notification email complete when configured", () => {
    const progress = evaluateOnboardingProgress("company-1", settings);
    expect(progress.notification_email).toBe(true);
  });

  it("tracks manual widget steps from options", () => {
    const progress = evaluateOnboardingProgress("company-1", settings, {
      widgetCopied: true,
      widgetInstalled: false,
      widgetTested: true,
    });

    expect(progress.copy_widget).toBe(true);
    expect(progress.install_widget).toBe(false);
    expect(progress.test_widget).toBe(true);
    expect(isOnboardingComplete(progress)).toBe(false);
  });

  it("reports completion only when every step is done", () => {
    const complete = evaluateOnboardingProgress("company-1", settings, {
      widgetCopied: true,
      widgetInstalled: true,
      widgetTested: true,
    });

    expect(isOnboardingComplete(complete)).toBe(true);
    expect(countCompletedSteps(complete)).toBe(ONBOARDING_STEPS.length);
  });
});
