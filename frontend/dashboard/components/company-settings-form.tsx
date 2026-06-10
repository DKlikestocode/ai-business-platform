"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchCompanySettings, updateCompanySettings } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { markOnboardingStepComplete } from "@/lib/onboarding";
import type { CompanySettings } from "@/lib/types";
import {
  buildWidgetEmbedSnippet,
  getPublicApiBaseUrl,
} from "@/lib/widget-embed";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "full",
    timeStyle: "short",
  }).format(new Date(value));
}

export function CompanySettingsForm() {
  const { company } = useAuth();
  const [settings, setSettings] = useState<CompanySettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);

  const loadSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCompanySettings();
      setSettings(data);
    } catch (err) {
      setError(formatUserFacingError(err, "Failed to load settings."));
    } finally {
      setLoading(false);
    }
  }, []);

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
      setSuccess("Settings saved.");
    } catch (err) {
      setError(formatUserFacingError(err, "Failed to save settings."));
    } finally {
      setSaving(false);
    }
  }

  async function handleCopyEmbed() {
    if (!settings) {
      return;
    }

    const snippet = buildWidgetEmbedSnippet(
      settings.slug,
      getPublicApiBaseUrl(),
    );

    try {
      await navigator.clipboard.writeText(snippet);
      if (company) {
        markOnboardingStepComplete(company.id, "copy_widget");
      }
      setCopyMessage("Copied to clipboard.");
    } catch {
      setCopyMessage("Unable to copy. Select the snippet manually.");
    }

    window.setTimeout(() => setCopyMessage(null), 2500);
  }

  function updateField<K extends keyof CompanySettings>(
    key: K,
    value: CompanySettings[K],
  ) {
    setSettings((current) => (current ? { ...current, [key]: value } : current));
    setSuccess(null);
  }

  if (loading) {
    return <LoadingState label="Loading settings..." />;
  }

  if (error && !settings) {
    return <AlertBanner>{error}</AlertBanner>;
  }

  if (!settings) {
    return <div className="empty-state">Settings not found.</div>;
  }

  const embedSnippet = buildWidgetEmbedSnippet(
    settings.slug,
    getPublicApiBaseUrl(),
  );

  return (
    <div className="stack">
      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {success ? <AlertBanner variant="success">{success}</AlertBanner> : null}

      <form className="card settings-form" onSubmit={(event) => void handleSubmit(event)}>
        <h3 className="card-title">Company profile</h3>
        <div className="settings-grid">
          <label className="field">
            <span>Name</span>
            <input
              className="input"
              value={settings.name}
              onChange={(event) => updateField("name", event.target.value)}
              required
            />
          </label>
          <label className="field">
            <span>Email</span>
            <input
              className="input"
              type="email"
              value={settings.email}
              onChange={(event) => updateField("email", event.target.value)}
              required
            />
          </label>
          <label className="field">
            <span>Phone</span>
            <input
              className="input"
              value={settings.phone ?? ""}
              onChange={(event) =>
                updateField("phone", event.target.value || null)
              }
            />
          </label>
          <div className="field">
            <span>Slug</span>
            <p className="read-only-value">
              <code>{settings.slug}</code>
            </p>
          </div>
          <div className="field">
            <span>Created</span>
            <p className="read-only-value muted">
              {formatDate(settings.created_at)}
            </p>
          </div>
        </div>

        <h3 className="card-title">Lead notifications</h3>
        <div className="settings-grid">
          <label className="field">
            <span>Notification email</span>
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
              placeholder="Defaults to company email"
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
            <span>Notify on qualified leads</span>
          </label>
          <label className="field checkbox-field">
            <input
              type="checkbox"
              checked={settings.notify_on_contactable_lead}
              onChange={(event) =>
                updateField("notify_on_contactable_lead", event.target.checked)
              }
            />
            <span>Notify on contactable leads above threshold</span>
          </label>
          <label className="field">
            <span>Contactable lead score threshold</span>
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
            {saving ? "Saving..." : "Save settings"}
          </button>
        </div>
      </form>

      <div className="card">
        <div className="embed-header">
          <h3 className="card-title">Website widget embed</h3>
          <button
            type="button"
            className="button secondary"
            onClick={() => void handleCopyEmbed()}
          >
            Copy snippet
          </button>
        </div>
        <p className="muted">
          Add this snippet to your website. The widget uses slug{" "}
          <code>{settings.slug}</code> to route messages to your company.
        </p>
        {copyMessage ? <div className="notice">{copyMessage}</div> : null}
        <pre className="embed-snippet">
          <code>{embedSnippet}</code>
        </pre>
      </div>
    </div>
  );
}
