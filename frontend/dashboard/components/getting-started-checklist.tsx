"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { fetchCompanySettings } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import {
  ONBOARDING_STEPS,
  countCompletedSteps,
  evaluateOnboardingProgress,
  isOnboardingComplete,
  markOnboardingStepComplete,
  type OnboardingStepId,
} from "@/lib/onboarding";
import type { CompanySettings } from "@/lib/types";

export function GettingStartedChecklist() {
  const { user, company, loading: authLoading } = useAuth();
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
      setError(formatUserFacingError(err, "Failed to load setup progress."));
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (authLoading) {
      return;
    }
    void load();
  }, [authLoading, load, refreshKey]);

  if (authLoading || (loading && !settings)) {
    return <LoadingState label="Loading your setup checklist..." />;
  }

  if (!user || !company) {
    return (
      <AlertBanner>
        Sign in to view your getting started checklist.
      </AlertBanner>
    );
  }

  const progress = evaluateOnboardingProgress(company.id, settings);
  const completed = countCompletedSteps(progress);
  const allDone = isOnboardingComplete(progress);

  function handleManualComplete(step: OnboardingStepId) {
    markOnboardingStepComplete(company.id, step);
    setRefreshKey((value) => value + 1);
  }

  return (
    <div className="stack">
      <PageHeader
        title="Getting started"
        description="Complete these steps to launch your pilot customer."
      >
        <div className="progress-pill">
          {completed}/{ONBOARDING_STEPS.length} complete
        </div>
      </PageHeader>

      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {allDone ? (
        <AlertBanner variant="success">
          Your pilot workspace is ready. New leads will appear on the Leads page.
        </AlertBanner>
      ) : null}

      <div className="checklist">
        {ONBOARDING_STEPS.map((step, index) => {
          const done = progress[step.id];
          return (
            <article
              key={step.id}
              className={`checklist-item card ${done ? "done" : ""}`}
            >
              <div className="checklist-index">{index + 1}</div>
              <div className="checklist-body">
                <div className="checklist-title-row">
                  <h3>{step.title}</h3>
                  <span className={`checklist-status ${done ? "done" : ""}`}>
                    {done ? "Done" : "To do"}
                  </span>
                </div>
                <p className="muted">{step.description}</p>
                {company.slug && step.id === "copy_widget" ? (
                  <p className="muted">
                    Company slug: <code>{company.slug}</code>
                  </p>
                ) : null}
                <div className="checklist-actions">
                  {step.href && step.actionLabel ? (
                    <Link href={step.href} className="button secondary">
                      {step.actionLabel}
                    </Link>
                  ) : null}
                  {step.id === "install_widget" && !done ? (
                    <button
                      type="button"
                      className="button secondary"
                      onClick={() => handleManualComplete("install_widget")}
                    >
                      Mark installed
                    </button>
                  ) : null}
                </div>
              </div>
            </article>
          );
        })}
      </div>

      <div className="card">
        <h3 className="card-title">Next steps</h3>
        <p className="muted">
          After the widget is live, monitor incoming leads, tune notification
          thresholds in Settings, and share the dashboard with your team.
        </p>
        <div className="checklist-actions">
          <Link href="/leads" className="button">
            Open leads
          </Link>
          <Link href="/settings" className="button secondary">
            Company settings
          </Link>
        </div>
      </div>
    </div>
  );
}
