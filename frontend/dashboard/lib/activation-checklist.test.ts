import { describe, expect, it } from "vitest";

import {
  ACTIVATION_CHECKLIST_STEPS,
  countActivationChecklistSteps,
  evaluateActivationChecklist,
  isActivationChecklistComplete,
  isAwaitingFirstWebsiteInquiry,
  isAwaitingWebsiteLive,
  shouldShowGettingStartedNav,
} from "@/lib/activation-checklist";
import {
  isOnboardingComplete,
  markOnboardingStepComplete,
  evaluateOnboardingProgress,
} from "@/lib/onboarding";
import type {
  Company,
  CompanyActivation,
  CompanySettings,
  CurrentUser,
} from "@/lib/types";

const company: Company = {
  id: "company-1",
  name: "Acme",
  slug: "acme",
  email: "hello@acme.co",
  phone: null,
  created_at: "2026-06-10T12:00:00Z",
};

const user: CurrentUser = {
  id: "user-1",
  company_id: company.id,
  first_name: "Alex",
  last_name: "Owner",
  email: "alex@acme.co",
  role: "owner",
  is_active: true,
  created_at: "2026-06-10T12:00:00Z",
};

const settings: CompanySettings = {
  name: "Acme",
  slug: "acme",
  email: "hello@acme.co",
  phone: null,
  notification_email: "alerts@acme.co",
  notification_min_urgency: "medium" as const,
  service_area_center: null,
  service_radius_km: null,
  trade: null,
  email_delivery_provider: "logging",
  email_delivery_ready: true,
  email_delivery_sends_real_email: false,
  created_at: "2026-06-10T12:00:00Z",
};

function buildActivation(
  overrides: Partial<CompanyActivation> = {},
): CompanyActivation {
  return {
    status: "awaiting_widget",
    notification_configured: true,
    website_url: null,
    widget_live_at: null,
    widget_last_seen_at: null,
    widget_last_origin: null,
    first_website_inquiry_at: null,
    install: {
      company_slug: "acme",
      embed_snippet:
        '<div data-install-token="secret"></div><script src="/widget.js"></script>',
    },
    updated_at: "2026-06-10T12:00:00Z",
    ...overrides,
  };
}

describe("activation checklist", () => {
  it("ignores stale localStorage when activation is awaiting_widget", () => {
    markOnboardingStepComplete(company.id, "copy_widget");
    markOnboardingStepComplete(company.id, "install_widget");
    markOnboardingStepComplete(company.id, "test_widget");

    const legacyProgress = evaluateOnboardingProgress(company.id, settings, {
      widgetCopied: true,
      widgetInstalled: true,
      widgetTested: true,
    });

    const progress = evaluateActivationChecklist({
      company,
      user,
      settings,
      activation: buildActivation({ status: "awaiting_widget" }),
    });

    expect(isOnboardingComplete(legacyProgress)).toBe(true);
    expect(isActivationChecklistComplete(progress)).toBe(false);
    expect(countActivationChecklistSteps(progress)).toBe(4);
    expect(progress.install_widget).toBe(false);
  });

  it("reports full progress only when activation is live and first inquiry arrived", () => {
    const progress = evaluateActivationChecklist({
      company,
      user,
      settings,
      activation: buildActivation({
        status: "live",
        widget_last_seen_at: "2026-06-10T13:00:00Z",
        widget_last_origin: "https://acme.co",
        first_website_inquiry_at: "2026-06-11T10:00:00Z",
      }),
    });

    expect(isActivationChecklistComplete(progress)).toBe(true);
    expect(countActivationChecklistSteps(progress)).toBe(
      ACTIVATION_CHECKLIST_STEPS.length,
    );
  });

  it("keeps checklist open when widget is live but no website inquiry yet", () => {
    const progress = evaluateActivationChecklist({
      company,
      user,
      settings,
      activation: buildActivation({
        status: "live",
        widget_last_seen_at: "2026-06-10T13:00:00Z",
        widget_last_origin: "https://acme.co",
      }),
    });

    expect(progress.install_widget).toBe(true);
    expect(progress.first_website_inquiry).toBe(false);
    expect(isActivationChecklistComplete(progress)).toBe(false);
    expect(countActivationChecklistSteps(progress)).toBe(5);
  });

  it("does not treat stale activation as complete", () => {
    const progress = evaluateActivationChecklist({
      company,
      user,
      settings,
      activation: buildActivation({
        status: "stale",
        widget_last_seen_at: "2026-06-01T10:00:00Z",
        widget_last_origin: "https://acme.co",
      }),
    });

    expect(progress.install_widget).toBe(false);
    expect(isActivationChecklistComplete(progress)).toBe(false);
    expect(countActivationChecklistSteps(progress)).toBe(4);
  });

  it("marks copy_widget incomplete without a server embed snippet", () => {
    const progress = evaluateActivationChecklist({
      company,
      user,
      settings,
      activation: buildActivation({
        install: {
          company_slug: "acme",
          embed_snippet: "",
        },
      }),
    });

    expect(progress.copy_widget).toBe(false);
    expect(countActivationChecklistSteps(progress)).toBe(3);
  });

  it("marks notification_email incomplete when missing from settings", () => {
    const progress = evaluateActivationChecklist({
      company,
      user,
      settings: { ...settings, notification_email: null, email: "" },
      activation: buildActivation({
        notification_configured: false,
        status: "setup_incomplete",
      }),
    });

    expect(progress.notification_email).toBe(false);
    expect(progress.copy_widget).toBe(false);
  });

  it("marks notification_email complete when company email is configured", () => {
    const progress = evaluateActivationChecklist({
      company,
      user,
      settings: { ...settings, notification_email: null, email: "hello@acme.co" },
      activation: buildActivation({
        notification_configured: false,
        status: "setup_incomplete",
      }),
    });

    expect(progress.notification_email).toBe(true);
  });

  it("marks copy_widget incomplete when install metadata is missing", () => {
    const progress = evaluateActivationChecklist({
      company,
      user,
      settings,
      activation: {
        ...buildActivation(),
        install: undefined as unknown as CompanyActivation["install"],
      },
    });

    expect(progress.copy_widget).toBe(false);
    expect(countActivationChecklistSteps(progress)).toBe(3);
  });

  it("detects awaiting website live state", () => {
    const progress = evaluateActivationChecklist({
      company,
      user,
      settings,
      activation: buildActivation({ status: "awaiting_widget" }),
    });

    expect(isAwaitingWebsiteLive(progress, "awaiting_widget")).toBe(true);
    expect(isAwaitingWebsiteLive(progress, "live")).toBe(false);
  });

  it("detects awaiting first website inquiry after widget is live", () => {
    const progress = evaluateActivationChecklist({
      company,
      user,
      settings,
      activation: buildActivation({
        status: "live",
        widget_last_seen_at: "2026-06-10T13:00:00Z",
      }),
    });

    expect(isAwaitingFirstWebsiteInquiry(progress)).toBe(true);
  });

  it("hides getting started nav while setup data is still loading", () => {
    expect(
      shouldShowGettingStartedNav({
        company,
        user,
        settings,
        activation: undefined,
      }),
    ).toBe(false);
  });

  it("hides getting started nav when checklist is complete and chat is live", () => {
    expect(
      shouldShowGettingStartedNav({
        company,
        user,
        settings,
        activation: buildActivation({
          status: "live",
          widget_last_seen_at: "2026-06-10T13:00:00Z",
          widget_last_origin: "https://acme.co",
          first_website_inquiry_at: "2026-06-11T10:00:00Z",
        }),
      }),
    ).toBe(false);
  });

  it("keeps getting started nav visible when widget is live but inquiry is missing", () => {
    expect(
      shouldShowGettingStartedNav({
        company,
        user,
        settings,
        activation: buildActivation({
          status: "live",
          widget_last_seen_at: "2026-06-10T13:00:00Z",
          widget_last_origin: "https://acme.co",
        }),
      }),
    ).toBe(true);
  });
});
