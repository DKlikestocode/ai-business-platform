"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useTranslations } from "next-intl";

import {
  ApiError,
  clearSession,
  establishSession,
  fetchCompany,
  fetchCurrentUser,
  login as loginRequest,
  setUnauthorizedHandler,
} from "@/lib/api";
import { getAccessToken, setAccessToken } from "@/lib/auth-storage";
import {
  readDashboardNavState,
  resolveAuthenticatedHomePathFromCache,
  type AuthenticatedHomePath,
  type DashboardNavState,
} from "@/lib/dashboard-nav";
import {
  clearDashboardCache,
  loadCachedCompanyActivation,
  loadCachedCompanySettings,
} from "@/lib/dashboard-cache";
import type { Company, CurrentUser } from "@/lib/types";
import { useRouter } from "@/i18n/navigation";

interface AuthSession {
  user: CurrentUser;
  company: Company;
  homePath: AuthenticatedHomePath;
}

interface AuthContextValue {
  user: CurrentUser | null;
  company: Company | null;
  loading: boolean;
  error: string | null;
  dashboardNavReady: boolean;
  showGettingStartedNav: boolean;
  login: (email: string, password: string) => Promise<AuthSession>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  refreshDashboardNav: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const EMPTY_DASHBOARD_NAV: DashboardNavState = {
  ready: false,
  showGettingStarted: false,
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const tAuth = useTranslations("auth");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardNav, setDashboardNav] =
    useState<DashboardNavState>(EMPTY_DASHBOARD_NAV);
  const userRef = useRef<CurrentUser | null>(null);

  useEffect(() => {
    userRef.current = user;
  }, [user]);

  const syncDashboardNav = useCallback(
    (
      currentUser: CurrentUser | null,
      companyData: Company | null,
    ): DashboardNavState => {
      const nextState = readDashboardNavState(currentUser, companyData);
      setDashboardNav(nextState);
      return nextState;
    },
    [],
  );

  const refreshDashboardNav = useCallback(() => {
    syncDashboardNav(user, company);
  }, [company, syncDashboardNav, user]);

  const logout = useCallback(async () => {
    setUser(null);
    setCompany(null);
    setError(null);
    setDashboardNav(EMPTY_DASHBOARD_NAV);
    clearDashboardCache();
    try {
      await clearSession();
    } catch {
      // Session cookie cleanup is best-effort during logout.
    }
    router.replace("/login");
  }, [router]);

  const prefetchDashboardData = useCallback(async () => {
    await Promise.all([
      loadCachedCompanySettings(),
      loadCachedCompanyActivation(),
    ]);
  }, []);

  const establishAuthenticatedSession = useCallback(
    async (
      currentUser: CurrentUser,
      companyData: Company,
    ): Promise<AuthSession> => {
      setUser(currentUser);
      setCompany(companyData);
      await prefetchDashboardData();
      syncDashboardNav(currentUser, companyData);
      return {
        user: currentUser,
        company: companyData,
        homePath: resolveAuthenticatedHomePathFromCache(
          currentUser,
          companyData,
        ),
      };
    },
    [prefetchDashboardData, syncDashboardNav],
  );

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setUser(null);
      setCompany(null);
      setDashboardNav(EMPTY_DASHBOARD_NAV);
      setLoading(false);
      return;
    }

    const hasExistingSession = Boolean(userRef.current);
    if (!hasExistingSession) {
      setLoading(true);
    }
    setError(null);
    try {
      const currentUser = await fetchCurrentUser();
      const companyData = await fetchCompany(currentUser.company_id);
      await establishAuthenticatedSession(currentUser, companyData);
    } catch (err) {
      setUser(null);
      setCompany(null);
      setDashboardNav(EMPTY_DASHBOARD_NAV);
      if (err instanceof ApiError && err.status === 401) {
        await clearSession();
      } else {
        setError(
          err instanceof Error ? err.message : tAuth("loadUserFailed"),
        );
      }
    } finally {
      setLoading(false);
    }
  }, [establishAuthenticatedSession, tAuth]);

  const login = useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        const tokenResponse = await loginRequest({ email, password });
        setAccessToken(tokenResponse.access_token);
        await establishSession();
        const currentUser = await fetchCurrentUser();
        const companyData = await fetchCompany(currentUser.company_id);
        return await establishAuthenticatedSession(currentUser, companyData);
      } catch (err) {
        setUser(null);
        setCompany(null);
        setDashboardNav(EMPTY_DASHBOARD_NAV);
        setError(err instanceof Error ? err.message : tAuth("loginFailed"));
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [establishAuthenticatedSession, tAuth],
  );

  useEffect(() => {
    setUnauthorizedHandler(() => {
      void logout();
    });

    return () => {
      setUnauthorizedHandler(null);
    };
  }, [logout]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const value = useMemo(
    () => ({
      user,
      company,
      loading,
      error,
      dashboardNavReady: dashboardNav.ready,
      showGettingStartedNav: dashboardNav.showGettingStarted,
      login,
      logout,
      refresh,
      refreshDashboardNav,
    }),
    [
      user,
      company,
      loading,
      error,
      dashboardNav.ready,
      dashboardNav.showGettingStarted,
      login,
      logout,
      refresh,
      refreshDashboardNav,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }
  return context;
}

export function CompanyLabel() {
  const { company, user, loading } = useAuth();
  const t = useTranslations("auth");

  if (!user || !company) {
    return loading ? (
      <p className="company-label muted" aria-hidden="true">
        {"\u00a0"}
      </p>
    ) : null;
  }

  return (
    <p className="company-label">
      {t("signedInAs")} <span>{user.first_name} {user.last_name}</span>
      {" · "}
      <span>{company.name}</span>
    </p>
  );
}
