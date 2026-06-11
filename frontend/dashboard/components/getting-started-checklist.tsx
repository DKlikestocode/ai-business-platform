"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { fetchCompanySettings } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import {
  ONBOARDING_STEPS,
  countCompletedSteps,
  evaluateOnboardingProgress,
  isOnboardingComplete,
  markOnboardingStepComplete,
  type OnboardingStepId,
} from "@/lib/onboarding";
import type { CompanySettings } from "@/lib/types";
import { Link } from "@/i18n/navigation";

export function GettingStartedChecklist() {
  const { user, company, loading: authLoading } = useAuth();
  const t = useTranslations("gettingStarted");
  const tCommon = useTranslations("common");
  const tOnboarding = useTranslations("onboarding.steps");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const [settings, setSettings] = useState<CompanySettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const load = useCallback(async () => {
    if (!user) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCompanySettings();
      setSettings(data);
    } catch (err) {
      setError(formatUserFacingError(err, t("loadFailed"), errorMessages));
    } finally {
      setLoading(false);
    }
  }, [user, t, errorMessages]);

  useEffect(() => {
    if (authLoading) {
      return;
    }
    void load();
  }, [authLoading, load, refreshKey]);

  if (authLoading || (loading && !settings)) {
    return <LoadingState label={t("loading")} />;
  }

  if (!user || !company) {
    return <AlertBanner>{t("signInRequired")}</AlertBanner>;
  }

  const activeCompany = company;

  const progress = evaluateOnboardingProgress(activeCompany.id, settings);
  const completed = countCompletedSteps(progress);
  const allDone = isOnboardingComplete(progress);
  const nextStep = ONBOARDING_STEPS.find((step) => !progress[step.id]);
  const welcomeName = activeCompany.name?.trim() || user.first_name;

  function handleManualComplete(step: OnboardingStepId) {
    markOnboardingStepComplete(activeCompany.id, step);
    setRefreshKey((value) => value + 1);
  }

  return (
    <div className="stack">
      <PageHeader title={t("title")} description={t("description")}>
        <div className="progress-pill">
          {t("progress", {
            completed,
            total: ONBOARDING_STEPS.length,
          })}
        </div>
      </PageHeader>

      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {allDone ? (
        <AlertBanner variant="success">{t("allDone")}</AlertBanner>
      ) : null}

      <section className="welcome-banner card" aria-labelledby="welcome-banner-title">
        <h3 id="welcome-banner-title" className="welcome-banner-title">
          {t("welcomeTitle", { name: welcomeName })}
        </h3>
        <p className="welcome-banner-lead muted">{t("welcomeLead")}</p>
        {nextStep ? (
          <div className="welcome-banner-next">
            <p className="welcome-banner-next-label">{t("welcomeNextStepLabel")}</p>
            <p className="welcome-banner-next-title">
              {tOnboarding(`${nextStep.id}.title`)}
            </p>
            {nextStep.href ? (
              <Link href={nextStep.href} className="button">
                {tOnboarding(`${nextStep.id}.action`)}
              </Link>
            ) : null}
          </div>
        ) : (
          <p className="muted">{t("welcomeAllDone")}</p>
        )}
      </section>

      <div className="checklist">
        {ONBOARDING_STEPS.map((step, index) => {
          const done = progress[step.id];
          const stepKey = step.id;
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
                <p className="muted">{tOnboarding(`${stepKey}.description`)}</p>
                {activeCompany.slug && step.id === "copy_widget" ? (
                  <p className="muted">
                    {t("companySlug")} <code>{activeCompany.slug}</code>
                  </p>
                ) : null}
                <div className="checklist-actions">
                  {step.href ? (
                    <Link href={step.href} className="button secondary">
                      {tOnboarding(`${stepKey}.action`)}
                    </Link>
                  ) : null}
                  {step.id === "install_widget" && !done ? (
                    <button
                      type="button"
                      className="button secondary"
                      onClick={() => handleManualComplete("install_widget")}
                    >
                      {tOnboarding("install_widget.markInstalled")}
                    </button>
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
        </div>
      </div>
    </div>
  );
}
