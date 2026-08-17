import { describe, expect, it, beforeEach } from "vitest";

import {
  readDashboardNavState,
  resolveAuthenticatedHomePathFromCache,
} from "@/lib/dashboard-nav";
import {
  clearDashboardCache,
  setDashboardCache,
  COMPANY_ACTIVATION_CACHE_KEY,
  COMPANY_SETTINGS_CACHE_KEY,
} from "@/lib/dashboard-cache";
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
  notification_min_urgency: "medium",
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

describe("dashboard-nav", () => {
  beforeEach(() => {
    clearDashboardCache();
  });

  it("keeps nav hidden while dashboard data is missing", () => {
    expect(readDashboardNavState(user, company)).toEqual({
      ready: false,
      showGettingStarted: false,
    });
  });

  it("routes completed accounts to the inbox", () => {
    setDashboardCache(COMPANY_SETTINGS_CACHE_KEY, settings);
    setDashboardCache(
      COMPANY_ACTIVATION_CACHE_KEY,
      buildActivation({
        status: "live",
        widget_last_seen_at: "2026-06-10T13:00:00Z",
        widget_last_origin: "https://acme.co",
        first_website_inquiry_at: "2026-06-11T10:00:00Z",
      }),
    );

    expect(readDashboardNavState(user, company)).toEqual({
      ready: true,
      showGettingStarted: false,
    });
    expect(resolveAuthenticatedHomePathFromCache(user, company)).toBe("/intake");
  });

  it("routes all accounts to the inbox", () => {
    setDashboardCache(COMPANY_SETTINGS_CACHE_KEY, settings);
    setDashboardCache(
      COMPANY_ACTIVATION_CACHE_KEY,
      buildActivation({
        status: "awaiting_widget",
      }),
    );

    expect(resolveAuthenticatedHomePathFromCache(user, company)).toBe("/intake");
  });
});
