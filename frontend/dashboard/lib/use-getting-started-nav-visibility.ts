"use client";

import { useAuth } from "@/components/auth-provider";

export function useGettingStartedNavVisibility() {
  const {
    loading: authLoading,
    dashboardNavReady,
    showGettingStartedNav,
    refreshDashboardNav,
  } = useAuth();

  return {
    showGettingStarted: dashboardNavReady && showGettingStartedNav,
    activationLoading: authLoading || !dashboardNavReady,
    refreshDashboardNav,
  };
}
