"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchCompanyActivation } from "@/lib/api";
import {
  activationStatusClassName,
  embedSnippetIncludesInstallToken,
  formatActivationTimestamp,
} from "@/lib/activation-display";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import type { CompanyActivation } from "@/lib/types";

interface WidgetActivationPanelProps {
  reloadKey?: number;
}

export function WidgetActivationPanel({
  reloadKey = 0,
}: WidgetActivationPanelProps) {
  const locale = useLocale();
  const t = useTranslations("activation");
  const tSettings = useTranslations("settings");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const [activation, setActivation] = useState<CompanyActivation | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);

  const loadActivation = useCallback(
    async (options?: { refresh?: boolean }) => {
      const isRefresh = options?.refresh ?? false;
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      try {
        const data = await fetchCompanyActivation();
        setActivation(data);
      } catch (err) {
        setError(formatUserFacingError(err, t("loadFailed"), errorMessages));
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [t, errorMessages],
  );

  useEffect(() => {
    void loadActivation({ refresh: reloadKey > 0 });
  }, [loadActivation, reloadKey]);

  async function handleCopyEmbed() {
    if (!activation?.install.embed_snippet) {
      return;
    }

    try {
      await navigator.clipboard.writeText(activation.install.embed_snippet);
      setCopyMessage(tSettings("copied"));
    } catch {
      setCopyMessage(tSettings("copyFailed"));
    }

    window.setTimeout(() => setCopyMessage(null), 2500);
  }

  const lastSeen = activation
    ? formatActivationTimestamp(activation.widget_last_seen_at, locale)
    : null;
  const embedSnippet = activation?.install.embed_snippet ?? "";

  return (
    <div className="card stack">
      <div className="embed-header">
        <h3 className="card-title">{tSettings("widgetEmbed")}</h3>
        <div className="embed-header-actions">
          <button
            type="button"
            className="button secondary"
            onClick={() => void loadActivation({ refresh: true })}
            disabled={loading || refreshing}
          >
            {refreshing ? t("refreshing") : t("refresh")}
          </button>
          <button
            type="button"
            className="button secondary"
            onClick={() => void handleCopyEmbed()}
            disabled={loading || !embedSnippet}
          >
            {tSettings("copySnippet")}
          </button>
        </div>
      </div>

      <p className="muted">{tSettings("widgetDescription")}</p>

      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {copyMessage ? <div className="notice">{copyMessage}</div> : null}

      {loading && !activation ? (
        <div className="content-loading-panel">
          <LoadingState label={t("loading")} />
        </div>
      ) : null}

      {activation ? (
        <>
          <section aria-labelledby="activation-status-title">
            <h4 id="activation-status-title" className="activation-section-title">
              {t("statusTitle")}
            </h4>
            <div className={activationStatusClassName(activation.status)}>
              <p className="activation-status-message">
                {t(`status.${activation.status}`)}
              </p>
              {activation.status === "live" || activation.status === "stale" ? (
                <div className="activation-status-meta">
                  {activation.widget_last_origin ? (
                    <p className="muted">
                      {t("lastOrigin", {
                        origin: activation.widget_last_origin,
                      })}
                    </p>
                  ) : null}
                  {lastSeen ? (
                    <p className="muted">{t("lastSeen", { date: lastSeen })}</p>
                  ) : null}
                </div>
              ) : null}
            </div>
          </section>

          <section aria-labelledby="activation-embed-title">
            <h4 id="activation-embed-title" className="activation-section-title">
              {t("embedTitle")}
            </h4>
            {!embedSnippetIncludesInstallToken(embedSnippet) ? (
              <AlertBanner variant="info">{t("embedMissingInstallKey")}</AlertBanner>
            ) : null}
            <pre className="embed-snippet">
              <code>{embedSnippet}</code>
            </pre>
          </section>

          <section aria-labelledby="activation-install-guide-title">
            <h4 id="activation-install-guide-title" className="activation-section-title">
              {t("installGuideTitle")}
            </h4>
            <div className="install-guide">
              <article className="install-guide-item">
                <h5>{t("installHtmlTitle")}</h5>
                <p className="muted">{t("installHtmlBody")}</p>
              </article>
              <article className="install-guide-item">
                <h5>{t("installWordPressTitle")}</h5>
                <p className="muted">{t("installWordPressBody")}</p>
              </article>
              <article className="install-guide-item">
                <h5>{t("installAgencyTitle")}</h5>
                <p className="muted">{t("installAgencyBody")}</p>
              </article>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
