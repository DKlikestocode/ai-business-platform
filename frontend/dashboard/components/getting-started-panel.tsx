"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import {
  COMPANY_ACTIVATION_CACHE_KEY,
  COMPANY_SETTINGS_CACHE_KEY,
  getDashboardCache,
  loadCachedCompanyActivation,
  loadCachedCompanySettings,
} from "@/lib/dashboard-cache";
import {
  ACTIVATION_CHECKLIST_STEPS,
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
import { closeGettingStartedOverlay } from "@/lib/getting-started-overlay";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import type { CompanyActivation, CompanySettings } from "@/lib/types";
import { Link } from "@/i18n/navigation";
import { translateWithTradeOverride } from "@/lib/trade-copy";
import { tradeNamespace } from "@/lib/trades/types";

export function GettingStartedPanel() {
  const { user, company, loading: authLoading } = useAuth();
  const { refreshDashboardNav } = useGettingStartedNavVisibility();
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
        refreshDashboardNav();
      } catch (err) {
        setActivationError(
          formatUserFacingError(err, tActivation("loadFailed"), errorMessages),
        );
      } finally {
        setActivationRefreshing(false);
      }
    },
    [user, tActivation, errorMessages, refreshDashboardNav],
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
    isReady && company ? company.name?.trim() || user!.first_name : "";
  const activationRefreshLabelText = activationRefreshLabel(activation?.status, {
    refresh: tActivation("refresh"),
    refreshStale: tActivation("refreshStale"),
  });

  function handleNavigateAway() {
    closeGettingStartedOverlay();
  }

  return (
    <div className="getting-started-panel stack">
      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {activationError ? <AlertBanner>{activationError}</AlertBanner> : null}

      {isContentLoading ? (
        <div className="content-loading-panel">
          <LoadingState label={t("loading")} />
        </div>
      ) : null}

      {isReady && progress && company && user ? (
        <>
          {allDone ? (
            <AlertBanner variant="success">{t("allDone")}</AlertBanner>
          ) : widgetLive && awaitingFirstWebsiteInquiry ? (
            <AlertBanner>{t("widgetLiveAwaitingInquiry")}</AlertBanner>
          ) : null}

          <section className="getting-started-panel-intro">
            <h3 className="getting-started-panel-title">
              {t("welcomeTitle", { name: welcomeName })}
            </h3>
            <p className="muted getting-started-panel-lead">{tt("welcomeLead")}</p>
            {nextStep ? (
              <div className="getting-started-panel-next">
                <p className="getting-started-panel-next-label">
                  {t("welcomeNextStepLabel")}
                </p>
                <p className="getting-started-panel-next-title">
                  {tOnboarding(`${nextStep.id}.title`)}
                </p>
                {nextStep.href ? (
                  <Link
                    href={nextStep.href}
                    className="button"
                    onClick={handleNavigateAway}
                  >
                    {tOnboarding(`${nextStep.id}.action`)}
                  </Link>
                ) : null}
              </div>
            ) : allDone ? (
              <div className="getting-started-panel-next">
                <p className="muted">{t("firstWebsiteInquiryReached")}</p>
                <Link href="/leads" className="button" onClick={handleNavigateAway}>
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
            <section
              className="getting-started-panel-activation card"
              aria-labelledby="getting-started-activation-title"
            >
              <div className="embed-header">
                <h4 id="getting-started-activation-title" className="card-title">
                  {t("activationStatusTitle")}
                </h4>
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

          <ol className="getting-started-checklist">
            {ACTIVATION_CHECKLIST_STEPS.map((step, index) => {
              const done = progress[step.id];
              const stepKey = step.id as ActivationChecklistStepId;
              return (
                <li
                  key={step.id}
                  className={`getting-started-checklist-item card ${done ? "is-done" : ""}`}
                >
                  <div className="getting-started-checklist-index" aria-hidden="true">
                    {done ? "✓" : index + 1}
                  </div>
                  <div className="getting-started-checklist-body">
                    <div className="getting-started-checklist-title-row">
                      <h4
                        className={`getting-started-checklist-title${done ? " is-done" : ""}`}
                      >
                        {tOnboarding(`${stepKey}.title`)}
                      </h4>
                      <span
                        className={`getting-started-checklist-status ${done ? "is-done" : ""}`}
                      >
                        {done ? tCommon("done") : tCommon("todo")}
                      </span>
                    </div>
                    <p className={`muted getting-started-checklist-copy${done ? " is-done" : ""}`}>
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
                    {step.href && !done ? (
                      <div className="getting-started-checklist-actions">
                        <Link
                          href={step.href}
                          className="button secondary"
                          onClick={handleNavigateAway}
                        >
                          {tOnboarding(`${stepKey}.action`)}
                        </Link>
                      </div>
                    ) : null}
                  </div>
                </li>
              );
            })}
          </ol>
        </>
      ) : null}
    </div>
  );
}
