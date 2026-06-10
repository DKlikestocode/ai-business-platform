"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
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
import type { Company, CurrentUser } from "@/lib/types";
import { useRouter } from "@/i18n/navigation";

interface AuthContextValue {
  user: CurrentUser | null;
  company: Company | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const tAuth = useTranslations("auth");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const logout = useCallback(async () => {
    setUser(null);
    setCompany(null);
    setError(null);
    try {
      await clearSession();
    } catch {
      // Session cookie cleanup is best-effort during logout.
    }
    router.replace("/login");
  }, [router]);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setUser(null);
      setCompany(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const currentUser = await fetchCurrentUser();
      const companyData = await fetchCompany(currentUser.company_id);
      setUser(currentUser);
      setCompany(companyData);
    } catch (err) {
      setUser(null);
      setCompany(null);
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
  }, [tAuth]);

  const login = useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        const tokenResponse = await loginRequest({ email, password });
        setAccessToken(tokenResponse.access_token);
        await establishSession();
        await refresh();
      } catch (err) {
        setUser(null);
        setCompany(null);
        setError(err instanceof Error ? err.message : tAuth("loginFailed"));
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [refresh, tAuth],
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
    () => ({ user, company, loading, error, login, logout, refresh }),
    [user, company, loading, error, login, logout, refresh],
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

  if (loading) {
    return <p className="company-label muted">{t("loadingAccount")}</p>;
  }

  if (!user || !company) {
    return null;
  }

  return (
    <p className="company-label">
      {t("signedInAs")} <span>{user.first_name} {user.last_name}</span>
      {" · "}
      <span>{company.name}</span>
    </p>
  );
}
