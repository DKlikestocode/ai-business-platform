"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { updateCompanySettings } from "@/lib/api";
import {
  COMPANY_SETTINGS_CACHE_KEY,
  getDashboardCache,
  loadCachedCompanySettings,
  setDashboardCache,
} from "@/lib/dashboard-cache";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import type { CompanySettings } from "@/lib/types";
import { WidgetActivationPanel } from "@/components/widget-activation-panel";

function formatDate(value: string, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    dateStyle: "full",
    timeStyle: "short",
  }).format(new Date(value));
}

export function CompanySettingsForm() {
  const { company } = useAuth();
  const locale = useLocale();
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const [settings, setSettings] = useState<CompanySettings | null>(() =>
    getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
  );
  const [loading, setLoading] = useState(
    () => !getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [activationReloadKey, setActivationReloadKey] = useState(0);

  const loadSettings = useCallback(async () => {
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
  }, [t, errorMessages]);

  useEffect(() => {
    void loadSettings();
  }, [loadSettings]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!settings) {
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await updateCompanySettings({
        name: settings.name,
        email: settings.email,
        phone: settings.phone,
        notification_email: settings.notification_email,
        notify_on_new_lead: settings.notify_on_new_lead,
        notify_on_contactable_lead: settings.notify_on_contactable_lead,
        contactable_lead_notification_threshold:
          settings.contactable_lead_notification_threshold,
      });
      setSettings(updated);
      setDashboardCache(COMPANY_SETTINGS_CACHE_KEY, updated);
      setSuccess(t("saved"));
      setActivationReloadKey((value) => value + 1);
    } catch (err) {
      setError(formatUserFacingError(err, t("saveFailed"), errorMessages));
    } finally {
      setSaving(false);
    }
  }

  function updateField<K extends keyof CompanySettings>(
    key: K,
    value: CompanySettings[K],
  ) {
    setSettings((current) => (current ? { ...current, [key]: value } : current));
    setSuccess(null);
  }

  return (
    <div className="stack">
      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {success ? <AlertBanner variant="success">{success}</AlertBanner> : null}

      {loading && !settings ? (
        <>
          <div className="card content-loading-panel">
            <LoadingState label={t("loading")} />
          </div>
          <div className="card content-loading-panel">
            <LoadingState label={t("loading")} />
          </div>
        </>
      ) : null}

      {!loading && !settings ? (
        <div className="empty-state">{t("notFound")}</div>
      ) : null}

      {settings ? (
      <>
      <form className="card settings-form" onSubmit={(event) => void handleSubmit(event)}>
        <h3 className="card-title">{t("companyProfile")}</h3>
        <div className="settings-grid">
          <label className="field">
            <span>{t("name")}</span>
            <input
              className="input"
              value={settings.name}
              onChange={(event) => updateField("name", event.target.value)}
              required
            />
          </label>
          <label className="field">
            <span>{tCommon("email")}</span>
            <input
              className="input"
              type="email"
              value={settings.email}
              onChange={(event) => updateField("email", event.target.value)}
              required
            />
          </label>
          <label className="field">
            <span>{t("phone")}</span>
            <input
              className="input"
              value={settings.phone ?? ""}
              onChange={(event) =>
                updateField("phone", event.target.value || null)
              }
            />
          </label>
          <div className="field">
            <span>{t("slug")}</span>
            <p className="read-only-value">
              <code>{settings.slug}</code>
            </p>
          </div>
          <div className="field">
            <span>{t("created")}</span>
            <p className="read-only-value muted">
              {formatDate(settings.created_at, locale)}
            </p>
          </div>
        </div>

        <h3 className="card-title">{t("leadNotifications")}</h3>
        <div className="settings-grid">
          <label className="field">
            <span>{t("notificationEmail")}</span>
            <input
              className="input"
              type="email"
              value={settings.notification_email ?? ""}
              onChange={(event) =>
                updateField(
                  "notification_email",
                  event.target.value || null,
                )
              }
              placeholder={t("notificationEmailPlaceholder")}
            />
          </label>
          <label className="field checkbox-field">
            <input
              type="checkbox"
              checked={settings.notify_on_new_lead}
              onChange={(event) =>
                updateField("notify_on_new_lead", event.target.checked)
              }
            />
            <span>{t("notifyQualified")}</span>
          </label>
          <label className="field checkbox-field">
            <input
              type="checkbox"
              checked={settings.notify_on_contactable_lead}
              onChange={(event) =>
                updateField("notify_on_contactable_lead", event.target.checked)
              }
            />
            <span>{t("notifyContactable")}</span>
          </label>
          <label className="field">
            <span>{t("contactableThreshold")}</span>
            <input
              className="input"
              type="number"
              min={0}
              max={100}
              value={settings.contactable_lead_notification_threshold}
              onChange={(event) =>
                updateField(
                  "contactable_lead_notification_threshold",
                  Number(event.target.value),
                )
              }
            />
          </label>
        </div>

        <div className="form-actions">
          <button type="submit" className="button" disabled={saving}>
            {saving ? t("saving") : t("saveSettings")}
          </button>
        </div>
      </form>

      <WidgetActivationPanel reloadKey={activationReloadKey} />
      </>
      ) : null}
    </div>
  );
}
