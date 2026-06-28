"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import {
  COMPANY_SETTINGS_CACHE_KEY,
  getDashboardCache,
  loadCachedCompanyActivation,
  loadCachedCompanySettings,
} from "@/lib/dashboard-cache";
import {
  ACTIVATION_CHECKLIST_STEPS,
  countActivationChecklistSteps,
  evaluateActivationChecklist,
  isActivationChecklistComplete,
  isAwaitingFirstWebsiteInquiry,
  isAwaitingWebsiteLive,
  type ActivationChecklistStepId,
} from "@/lib/activation-checklist";
import {
  ActivationStatusView,
  activationRefreshLabel,
} from "@/components/activation-status-view";
import { useGettingStartedNavVisibility } from "@/lib/use-getting-started-nav-visibility";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import type { CompanyActivation, CompanySettings } from "@/lib/types";
import { Link, useRouter } from "@/i18n/navigation";
import { translateWithTradeOverride } from "@/lib/trade-copy";
import { tradeNamespace } from "@/lib/trades/types";

export function GettingStartedChecklist() {
  const router = useRouter();
  const { user, company, loading: authLoading } = useAuth();
  const { showGettingStarted, activationLoading } =
    useGettingStartedNavVisibility();
  const locale = useLocale();
  const [settings, setSettings] = useState<CompanySettings | null>(() =>
    getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
  );
  const trade = settings?.trade ?? null;
  const t = useTranslations("gettingStarted");
  const tTrade = useTranslations(tradeNamespace(trade, "gettingStarted"));
  const tActivation = useTranslations("activation");
  const tCommon = useTranslations("common");
  const tOnboarding = useTranslations("onboarding.steps");
  const tErrors = useTranslations("errors");
  const errorMessages = useMemo(() => getErrorMessages(tErrors), [tErrors]);
  const tt = useCallback(
    (key: string) => translateWithTradeOverride(t, tTrade, key, Boolean(trade)),
    [trade, t, tTrade],
  );
  const [loading, setLoading] = useState(
    () => !getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
  );
  const [error, setError] = useState<string | null>(null);
  const [activation, setActivation] = useState<CompanyActivation | null>(null);
  const [activationError, setActivationError] = useState<string | null>(null);
  const [activationRefreshing, setActivationRefreshing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const load = useCallback(async () => {
    if (!user) {
      return;
    }
    const hasCache = Boolean(
      getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
    );
    if (!hasCache) {
      setLoading(true);
    }
    setError(null);
    try {
      const data = await loadCachedCompanySettings(setSettings);
      setSettings(data);
    } catch (err) {
      setError(formatUserFacingError(err, t("loadFailed"), errorMessages));
    } finally {
      setLoading(false);
    }
  }, [user, t, errorMessages]);

  const loadActivation = useCallback(
    async (options?: { showRefreshing?: boolean }) => {
      if (!user) {
        return;
      }

      if (options?.showRefreshing) {
        setActivationRefreshing(true);
      }
      setActivationError(null);
      try {
        const data = await loadCachedCompanyActivation();
        setActivation(data);
      } catch (err) {
        setActivationError(
          formatUserFacingError(err, tActivation("loadFailed"), errorMessages),
        );
      } finally {
        setActivationRefreshing(false);
      }
    },
    [user, tActivation, errorMessages],
  );

  useEffect(() => {
    if (authLoading) {
      return;
    }
    void load();
  }, [authLoading, load, refreshKey]);

  useEffect(() => {
    if (authLoading || !user) {
      return;
    }
    void loadActivation();
  }, [authLoading, user, loadActivation, refreshKey]);

  useEffect(() => {
    if (authLoading || !user || activationLoading || showGettingStarted) {
      return;
    }
    router.replace("/leads");
  }, [authLoading, user, activationLoading, showGettingStarted, router]);

  const isContentLoading = authLoading || (loading && !settings);
  const isReady = Boolean(!authLoading && user && company && settings);

  const progress = isReady
    ? evaluateActivationChecklist({
        company,
        user,
        settings,
        activation,
      })
    : null;
  const completed = progress ? countActivationChecklistSteps(progress) : 0;
  const allDone = progress ? isActivationChecklistComplete(progress) : false;
  const awaitingFirstWebsiteInquiry =
    progress ? isAwaitingFirstWebsiteInquiry(progress) : false;
  const widgetLive = progress?.install_widget ?? false;
  const awaitingWebsiteLive =
    progress && activation
      ? isAwaitingWebsiteLive(progress, activation.status)
      : false;
  const nextStep =
    progress && !allDone
      ? ACTIVATION_CHECKLIST_STEPS.find((step) => !progress[step.id])
      : undefined;
  const welcomeName =
    isReady && company
      ? company.name?.trim() || user!.first_name
      : "";
  const activationRefreshLabelText = activationRefreshLabel(activation?.status, {
    refresh: tActivation("refresh"),
    refreshStale: tActivation("refreshStale"),
  });

  return (
    <div className="stack">
      <PageHeader title={t("title")} description={tt("description")}>
        {isReady ? (
          <div className="progress-pill">
            {t("progress", {
              completed,
              total: ACTIVATION_CHECKLIST_STEPS.length,
            })}
          </div>
        ) : null}
      </PageHeader>

      {!authLoading && (!user || !company) ? (
        <AlertBanner>{t("signInRequired")}</AlertBanner>
      ) : null}
      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {activationError ? <AlertBanner>{activationError}</AlertBanner> : null}

      {isContentLoading ? (
        <>
          <section className="welcome-banner card content-loading-panel">
            <LoadingState label={t("loading")} />
          </section>
          <div className="checklist">
            {ACTIVATION_CHECKLIST_STEPS.map((step, index) => (
              <article key={step.id} className="checklist-item card">
                <div className="checklist-index">{index + 1}</div>
                <div className="checklist-body content-loading-panel">
                  <LoadingState label={t("loading")} />
                </div>
              </article>
            ))}
          </div>
        </>
      ) : null}

      {isReady && progress && company && user ? (
        <>
          {allDone ? (
            <AlertBanner variant="success">{t("allDone")}</AlertBanner>
          ) : widgetLive && awaitingFirstWebsiteInquiry ? (
            <AlertBanner>{t("widgetLiveAwaitingInquiry")}</AlertBanner>
          ) : null}

          <section
            className="welcome-banner card"
            aria-labelledby="welcome-banner-title"
          >
            <h3 id="welcome-banner-title" className="welcome-banner-title">
              {t("welcomeTitle", { name: welcomeName })}
            </h3>
            <p className="welcome-banner-lead muted">{tt("welcomeLead")}</p>
            {nextStep ? (
              <div className="welcome-banner-next">
                <p className="welcome-banner-next-label">
                  {t("welcomeNextStepLabel")}
                </p>
                <p className="welcome-banner-next-title">
                  {tOnboarding(`${nextStep.id}.title`)}
                </p>
                {nextStep.href ? (
                  <Link href={nextStep.href} className="button">
                    {tOnboarding(`${nextStep.id}.action`)}
                  </Link>
                ) : null}
              </div>
            ) : allDone ? (
              <div className="welcome-banner-next">
                <p className="muted">{t("firstWebsiteInquiryReached")}</p>
                <Link href="/leads" className="button">
                  {t("openLeads")}
                </Link>
              </div>
            ) : awaitingFirstWebsiteInquiry ? (
              <p className="muted">{t("awaitingFirstWebsiteInquiry")}</p>
            ) : awaitingWebsiteLive ? (
              <p className="muted">{t("awaitingWebsiteLive")}</p>
            ) : null}
          </section>

          {activation ? (
            <section className="card" aria-labelledby="getting-started-activation-title">
              <div className="embed-header">
                <h3 id="getting-started-activation-title" className="card-title">
                  {t("activationStatusTitle")}
                </h3>
                <button
                  type="button"
                  className="button secondary"
                  onClick={() => void loadActivation({ showRefreshing: true })}
                  disabled={activationRefreshing}
                >
                  {activationRefreshing
                    ? tActivation("refreshing")
                    : activationRefreshLabelText}
                </button>
              </div>
              <ActivationStatusView activation={activation} locale={locale} />
              <p className="muted getting-started-activation-hint">
                {t("activationHint")}
              </p>
            </section>
          ) : null}

          <div className="checklist">
            {ACTIVATION_CHECKLIST_STEPS.map((step, index) => {
              const done = progress[step.id];
              const stepKey = step.id as ActivationChecklistStepId;
              return (
                <article
                  key={step.id}
                  className={`checklist-item card ${done ? "done" : ""}`}
                >
                  <div className="checklist-index">{index + 1}</div>
                  <div className="checklist-body">
                    <div className="checklist-title-row">
                      <h3>{tOnboarding(`${stepKey}.title`)}</h3>
                      <span className={`checklist-status ${done ? "done" : ""}`}>
                        {done ? tCommon("done") : tCommon("todo")}
                      </span>
                    </div>
                    <p className="muted">
                      {tOnboarding(`${stepKey}.description`)}
                    </p>
                    {step.id === "notification_email" ? (
                      <p className="muted">{t("notificationTestHint")}</p>
                    ) : null}
                    {step.id === "copy_widget" ? (
                      <p className="muted">{t("copyWidgetHint")}</p>
                    ) : null}
                    {step.id === "install_widget" && activation?.status === "live" ? (
                      <p className="muted">{t("installWidgetLiveHint")}</p>
                    ) : null}
                    {step.id === "first_website_inquiry" ? (
                      <p className="muted">{tt("firstWebsiteInquiryHint")}</p>
                    ) : null}
                    {company.slug && step.id === "copy_widget" ? (
                      <p className="muted">
                        {t("companySlug")} <code>{company.slug}</code>
                      </p>
                    ) : null}
                    <div className="checklist-actions">
                      {step.href ? (
                        <Link href={step.href} className="button secondary">
                          {tOnboarding(`${stepKey}.action`)}
                        </Link>
                      ) : null}
                    </div>
                  </div>
                </article>
              );
            })}
          </div>

          <div className="card">
            <h3 className="card-title">{t("nextStepsTitle")}</h3>
            <p className="muted">{t("nextStepsDescription")}</p>
            <div className="checklist-actions">
              <Link href="/leads" className="button">
                {t("openLeads")}
              </Link>
              <Link href="/settings" className="button secondary">
                {t("companySettings")}
              </Link>
              <Link href="/demo-chat" className="button secondary">
                {t("openSandboxChat")}
              </Link>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
