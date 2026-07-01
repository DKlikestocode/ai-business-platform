import { shouldShowGettingStartedNav } from "@/lib/activation-checklist";
import {
  COMPANY_ACTIVATION_CACHE_KEY,
  COMPANY_SETTINGS_CACHE_KEY,
  getDashboardCache,
} from "@/lib/dashboard-cache";
import type {
  Company,
  CompanyActivation,
  CompanySettings,
  CurrentUser,
} from "@/lib/types";

export type AuthenticatedHomePath = "/leads";

export interface DashboardNavState {
  ready: boolean;
  showGettingStarted: boolean;
}

export function readDashboardNavState(
  user: CurrentUser | null | undefined,
  company: Company | null | undefined,
): DashboardNavState {
  if (!user || !company) {
    return { ready: false, showGettingStarted: false };
  }

  const settings = getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY);
  const activation = getDashboardCache<CompanyActivation>(
    COMPANY_ACTIVATION_CACHE_KEY,
  );

  if (!settings || !activation) {
    return { ready: false, showGettingStarted: false };
  }

  return {
    ready: true,
    showGettingStarted: shouldShowGettingStartedNav({
      company,
      user,
      settings,
      activation,
    }),
  };
}

export function resolveAuthenticatedHomePathFromCache(
  _user: CurrentUser,
  _company: Company,
): AuthenticatedHomePath {
  return "/leads";
}
