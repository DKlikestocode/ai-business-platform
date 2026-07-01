"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { updateCompanySettings, sendTestNotification, ApiError } from "@/lib/api";
import {
  COMPANY_SETTINGS_CACHE_KEY,
  getDashboardCache,
  loadCachedCompanySettings,
  setDashboardCache,
} from "@/lib/dashboard-cache";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import {
  NOTIFICATION_MIN_URGENCY_LEVELS,
  type NotificationMinUrgency,
} from "@/lib/notification-min-urgency";
import {
  canSendTestNotification,
  isNotificationEmailDirty,
  normalizeNotificationEmail,
} from "@/lib/notification-settings";
import {
  isNotificationConfigured,
  resolveNotificationRecipient,
} from "@/lib/notification-recipient";
import type { CompanySettings } from "@/lib/types";
import { isCompanyTradeId } from "@/lib/trades/types";
import { WidgetActivationPanel } from "@/components/widget-activation-panel";
import { VoiceSetupPanel } from "@/components/voice-setup-panel";

export function CompanySettingsForm() {
  const { refresh } = useAuth();
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const errorMessages = useMemo(() => getErrorMessages(tErrors), [tErrors]);
  const [settings, setSettings] = useState<CompanySettings | null>(() =>
    getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
  );
  const [savedNotificationEmail, setSavedNotificationEmail] = useState<
    string | null
  >(
    () =>
      getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY)
        ?.notification_email ?? null,
  );
  const [loading, setLoading] = useState(
    () => !getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
  );
  const [saving, setSaving] = useState(false);
  const [testingNotification, setTestingNotification] = useState(false);
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
      setSavedNotificationEmail(data.notification_email);
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
        notification_min_urgency: settings.notification_min_urgency,
        service_area_center: settings.service_area_center,
        service_radius_km: settings.service_radius_km,
        trade: settings.trade,
      });
      setSettings(updated);
      setSavedNotificationEmail(updated.notification_email);
      setDashboardCache(COMPANY_SETTINGS_CACHE_KEY, updated);
      await refresh();
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

  const notificationsActive = isNotificationConfigured(settings);
  const notificationEmailDirty = isNotificationEmailDirty(
    savedNotificationEmail,
    settings?.notification_email,
  );
  const testNotificationEnabled = canSendTestNotification(settings, settings);

  async function handleTestNotification() {
    if (!testNotificationEnabled) {
      return;
    }

    setTestingNotification(true);
    setError(null);
    setSuccess(null);
    try {
      await sendTestNotification();
      setSuccess(
        t("testNotificationSuccess", {
          email: resolveNotificationRecipient(settings),
        }),
      );
    } catch (err) {
      if (err instanceof ApiError && err.status === 422) {
        setError(t("testNotificationMissingEmail"));
      } else {
        setError(
          formatUserFacingError(err, t("testNotificationFailed"), errorMessages),
        );
      }
    } finally {
      setTestingNotification(false);
    }
  }

  return (
    <div className="stack settings-page">
      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {success ? (
        <div className="success-fade-in">
          <AlertBanner variant="success">{success}</AlertBanner>
        </div>
      ) : null}

      {loading && !settings ? (
        <>
          <div className="card content-loading-panel content-fade-in">
            <LoadingState label={t("loading")} />
          </div>
          <div className="card content-loading-panel" aria-hidden="true" />
        </>
      ) : null}

      {!loading && !settings ? (
        <div className="empty-state">{t("notFound")}</div>
      ) : null}

      {settings ? (
      <div className="content-fade-in stack">
      <form className="card settings-form" onSubmit={(event) => void handleSubmit(event)}>
        <section className="settings-section" aria-labelledby="settings-profile-title">
          <h3 id="settings-profile-title" className="settings-section-title">
            {t("companyProfile")}
          </h3>
          <p className="muted field-hint settings-section-intro">{t("companyProfileHint")}</p>
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
              <p className="muted field-hint">{t("emailHint")}</p>
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
              <p className="muted field-hint">{t("phoneHint")}</p>
            </label>
            <label className="field">
              <span>{t("trade")}</span>
              <select
                className="input"
                value={settings.trade ?? ""}
                onChange={(event) =>
                  updateField(
                    "trade",
                    isCompanyTradeId(event.target.value) ? event.target.value : null,
                  )
                }
              >
                <option value="">{t("tradeOptions.general")}</option>
                <option value="skh">{t("tradeOptions.skh")}</option>
              </select>
              <p className="muted field-hint">{t("tradeHint")}</p>
            </label>
          </div>
        </section>

        <section className="settings-section" aria-labelledby="settings-service-area-title">
          <h3 id="settings-service-area-title" className="settings-section-title">
            {t("serviceArea")}
          </h3>
          <p className="muted field-hint settings-section-intro">{t("serviceAreaHint")}</p>
          <div className="settings-grid">
            <label className="field">
              <span>{t("serviceAreaCenter")}</span>
              <input
                className="input"
                value={settings.service_area_center ?? ""}
                onChange={(event) =>
                  updateField(
                    "service_area_center",
                    event.target.value.trim() || null,
                  )
                }
                placeholder={t("serviceAreaCenterPlaceholder")}
                inputMode="text"
                autoComplete="postal-code"
              />
              <p className="muted field-hint">{t("serviceAreaCenterHint")}</p>
            </label>
            <label className="field">
              <span>{t("serviceRadiusKm")}</span>
              <input
                className="input"
                type="number"
                min={1}
                max={500}
                value={settings.service_radius_km ?? ""}
                onChange={(event) =>
                  updateField(
                    "service_radius_km",
                    event.target.value ? Number(event.target.value) : null,
                  )
                }
                placeholder={t("serviceRadiusKmPlaceholder")}
              />
            </label>
          </div>
        </section>

        <section className="settings-section" aria-labelledby="settings-email-delivery-title">
          <h3 id="settings-email-delivery-title" className="settings-section-title">
            {t("emailDelivery")}
          </h3>
          <p className="muted field-hint settings-section-intro">{t("emailDeliveryHint")}</p>
          <div className="notification-status-row">
            <span
              className={
                settings.email_delivery_ready
                  ? "badge badge-contactable-yes"
                  : "badge badge-contactable-no"
              }
            >
              {settings.email_delivery_ready
                ? t("emailDeliveryReady")
                : t("emailDeliveryNotReady")}
            </span>
          </div>
          <p className="muted field-hint">
            {settings.email_delivery_provider === "resend"
              ? settings.email_delivery_sends_real_email
                ? t("emailDeliveryProviderResend")
                : t("emailDeliveryProviderResendIncomplete")
              : t("emailDeliveryProviderLogging")}
          </p>
          {settings.email_delivery_provider === "resend" &&
          !settings.email_delivery_ready ? (
            <p className="muted field-hint">{t("emailDeliveryResendSetup")}</p>
          ) : null}
        </section>

        <section
          className="settings-section settings-notification-section"
          aria-labelledby="lead-notifications"
        >
          <h3 id="lead-notifications" className="settings-section-title">
            {t("leadNotifications")}
          </h3>
          <div className="notification-status-row settings-notification-header">
            <span
              className={
                notificationsActive
                  ? "badge badge-contactable-yes"
                  : "badge badge-contactable-no"
              }
            >
              {notificationsActive
                ? t("notificationsActive")
                : t("notificationsInactive")}
            </span>
            <div className="notification-test-actions">
              {notificationEmailDirty ? (
                <p className="muted field-hint">{t("testNotificationSaveFirst")}</p>
              ) : null}
              <button
                type="button"
                className="button secondary"
                onClick={() => void handleTestNotification()}
                disabled={testingNotification || !testNotificationEnabled}
              >
                {testingNotification
                  ? t("testNotificationSending")
                  : t("testNotification")}
              </button>
            </div>
          </div>
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
              {!normalizeNotificationEmail(savedNotificationEmail) ? (
                <p className="muted field-hint">{t("notificationEmailFallbackHint")}</p>
              ) : null}
            </label>
            <label className="field">
              <span>{t("notificationMinUrgency")}</span>
              <select
                className="input"
                value={settings.notification_min_urgency}
                onChange={(event) =>
                  updateField(
                    "notification_min_urgency",
                    event.target.value as NotificationMinUrgency,
                  )
                }
              >
                {NOTIFICATION_MIN_URGENCY_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {t(`notificationMinUrgencyOptions.${level}`)}
                  </option>
                ))}
              </select>
              <p className="muted field-hint">{t("notificationMinUrgencyHint")}</p>
            </label>
          </div>
        </section>

        <div className="form-actions settings-form-actions">
          <button
            type="submit"
            className={`button${saving ? " is-saving" : ""}`}
            disabled={saving}
          >
            {saving ? t("saving") : t("saveSettings")}
          </button>
        </div>
      </form>

      <WidgetActivationPanel reloadKey={activationReloadKey} />
      {settings ? <VoiceSetupPanel companySlug={settings.slug} /> : null}
      </div>
      ) : null}
    </div>
  );
}
