import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchCompanySettings } from "@/lib/api";
import type { CompanySettings } from "@/lib/types";

import {
  COMPANY_SETTINGS_CACHE_KEY,
  clearDashboardCache,
  getDashboardCache,
  loadCachedCompanySettings,
  setDashboardCache,
} from "@/lib/dashboard-cache";

vi.mock("@/lib/api", () => ({
  fetchCompanySettings: vi.fn(),
}));

const settings: CompanySettings = {
  name: "Acme",
  slug: "acme",
  email: "hello@acme.co",
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

const updatedSettings: CompanySettings = {
  ...settings,
  name: "Acme Updated",
};

describe("dashboard-cache", () => {
  beforeEach(() => {
    clearDashboardCache();
    vi.mocked(fetchCompanySettings).mockReset();
  });

  it("stores and reads cached values by key", () => {
    setDashboardCache(COMPANY_SETTINGS_CACHE_KEY, settings);
    expect(getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY)).toEqual(
      settings,
    );
  });

  it("fetches company settings when cache is empty", async () => {
    vi.mocked(fetchCompanySettings).mockResolvedValue(settings);

    const result = await loadCachedCompanySettings();

    expect(result).toEqual(settings);
    expect(fetchCompanySettings).toHaveBeenCalledTimes(1);
    expect(getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY)).toEqual(
      settings,
    );
  });

  it("returns cached settings immediately and refreshes in the background", async () => {
    setDashboardCache(COMPANY_SETTINGS_CACHE_KEY, settings);
    vi.mocked(fetchCompanySettings).mockResolvedValue(updatedSettings);

    const onUpdate = vi.fn();
    const result = await loadCachedCompanySettings(onUpdate);

    expect(result).toEqual(settings);
    expect(fetchCompanySettings).toHaveBeenCalledTimes(1);

    await vi.waitFor(() => {
      expect(onUpdate).toHaveBeenCalledWith(updatedSettings);
    });

    expect(getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY)).toEqual(
      updatedSettings,
    );
  });

  it("keeps cached settings when background refresh fails", async () => {
    setDashboardCache(COMPANY_SETTINGS_CACHE_KEY, settings);
    vi.mocked(fetchCompanySettings).mockRejectedValue(new Error("network"));

    const onUpdate = vi.fn();
    const result = await loadCachedCompanySettings(onUpdate);

    expect(result).toEqual(settings);
    await new Promise((resolve) => setTimeout(resolve, 0));
    expect(onUpdate).not.toHaveBeenCalled();
    expect(getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY)).toEqual(
      settings,
    );
  });
});
