"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { shouldShowGettingStartedNav } from "@/lib/activation-checklist";
import {
  COMPANY_ACTIVATION_CACHE_KEY,
  COMPANY_SETTINGS_CACHE_KEY,
  getDashboardCache,
  loadCachedCompanyActivation,
  loadCachedCompanySettings,
} from "@/lib/dashboard-cache";
import type { CompanyActivation, CompanySettings } from "@/lib/types";
import { usePathname } from "@/i18n/navigation";

export function useGettingStartedNavVisibility() {
  const pathname = usePathname();
  const { user, company, loading: authLoading } = useAuth();
  const [settings, setSettings] = useState<CompanySettings | null>(() =>
    getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
  );
  const [activation, setActivation] = useState<CompanyActivation | null | undefined>(
    () => {
      const cached = getDashboardCache<CompanyActivation>(
        COMPANY_ACTIVATION_CACHE_KEY,
      );
      return cached ?? undefined;
    },
  );

  const load = useCallback(async () => {
    if (!user) {
      return;
    }

    try {
      const [settingsData, activationData] = await Promise.all([
        loadCachedCompanySettings(setSettings),
        loadCachedCompanyActivation(setActivation),
      ]);
      setSettings(settingsData);
      setActivation(activationData);
    } catch {
      setActivation((current) => (current === undefined ? null : current));
    }
  }, [user]);

  useEffect(() => {
    if (authLoading || !user) {
      return;
    }
    void load();
  }, [authLoading, user, load, pathname]);

  const activationLoading = Boolean(user) && activation === undefined;
  const showGettingStarted =
    authLoading ||
    !user ||
    !company ||
    activationLoading ||
    shouldShowGettingStartedNav({
      company,
      user,
      settings,
      activation: activation ?? null,
    });

  return {
    showGettingStarted,
    activationLoading: authLoading || activationLoading,
  };
}
