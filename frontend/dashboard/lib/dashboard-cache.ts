import { fetchCompanySettings, fetchCompanyActivation } from "@/lib/api";
import type { CompanyActivation, CompanySettings } from "@/lib/types";

export const COMPANY_SETTINGS_CACHE_KEY = "company-settings";
export const COMPANY_ACTIVATION_CACHE_KEY = "company-activation";

const cache = new Map<string, unknown>();

export function getDashboardCache<T>(key: string): T | null {
  const value = cache.get(key);
  return value === undefined ? null : (value as T);
}

export function setDashboardCache<T>(key: string, value: T): void {
  cache.set(key, value);
}

export function invalidateDashboardCache(key: string): void {
  cache.delete(key);
}

export function clearDashboardCache(): void {
  cache.clear();
}

export async function loadCachedCompanySettings(
  onUpdate?: (data: CompanySettings) => void,
): Promise<CompanySettings> {
  const cached = getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY);

  if (cached) {
    void fetchCompanySettings()
      .then((data) => {
        setDashboardCache(COMPANY_SETTINGS_CACHE_KEY, data);
        onUpdate?.(data);
      })
      .catch(() => {
        // Keep showing cached data when background refresh fails.
      });
    return cached;
  }

  const data = await fetchCompanySettings();
  setDashboardCache(COMPANY_SETTINGS_CACHE_KEY, data);
  return data;
}

export async function loadCachedCompanyActivation(
  onUpdate?: (data: CompanyActivation) => void,
): Promise<CompanyActivation> {
  const cached = getDashboardCache<CompanyActivation>(COMPANY_ACTIVATION_CACHE_KEY);

  if (cached) {
    void fetchCompanyActivation()
      .then((data) => {
        setDashboardCache(COMPANY_ACTIVATION_CACHE_KEY, data);
        onUpdate?.(data);
      })
      .catch(() => {
        // Keep showing cached data when background refresh fails.
      });
    return cached;
  }

  const data = await fetchCompanyActivation();
  setDashboardCache(COMPANY_ACTIVATION_CACHE_KEY, data);
  return data;
}
