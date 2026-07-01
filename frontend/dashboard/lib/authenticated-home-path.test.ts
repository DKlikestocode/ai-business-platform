import { describe, expect, it, vi } from "vitest";

import { resolveAuthenticatedHomePath } from "@/lib/authenticated-home-path";
import type {
  Company,
  CompanyActivation,
  CompanySettings,
  CurrentUser,
} from "@/lib/types";

vi.mock("@/lib/dashboard-cache", () => ({
  loadCachedCompanySettings: vi.fn(),
  loadCachedCompanyActivation: vi.fn(),
}));

import {
  loadCachedCompanyActivation,
  loadCachedCompanySettings,
} from "@/lib/dashboard-cache";

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

describe("resolveAuthenticatedHomePath", () => {
  it("routes completed accounts to the inbox", async () => {
    vi.mocked(loadCachedCompanySettings).mockResolvedValue(settings);
    vi.mocked(loadCachedCompanyActivation).mockResolvedValue(
      buildActivation({
        status: "live",
        widget_last_seen_at: "2026-06-10T13:00:00Z",
        widget_last_origin: "https://acme.co",
        first_website_inquiry_at: "2026-06-11T10:00:00Z",
      }),
    );

    await expect(resolveAuthenticatedHomePath(user, company)).resolves.toBe(
      "/leads",
    );
  });

  it("routes incomplete setup to getting started", async () => {
    vi.mocked(loadCachedCompanySettings).mockResolvedValue(settings);
    vi.mocked(loadCachedCompanyActivation).mockResolvedValue(buildActivation());

    await expect(resolveAuthenticatedHomePath(user, company)).resolves.toBe(
      "/getting-started",
    );
  });
});
