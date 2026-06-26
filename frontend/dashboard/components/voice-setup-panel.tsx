"use client";

import { useCallback, useMemo, useState } from "react";
import { useTranslations } from "next-intl";

import { AlertBanner } from "@/components/ui/alert-banner";
import { sendTestVoiceIntake } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import {
  buildVoiceMessageUrl,
  buildVoiceWebhookUrl,
} from "@/lib/voice-setup";
import { getPublicApiBaseUrl } from "@/lib/widget-embed";
import { Link } from "@/i18n/navigation";

interface VoiceSetupPanelProps {
  companySlug: string;
}

export function VoiceSetupPanel({ companySlug }: VoiceSetupPanelProps) {
  const t = useTranslations("settings");
  const tErrors = useTranslations("errors");
  const errorMessages = useMemo(() => getErrorMessages(tErrors), [tErrors]);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);
  const [testingIntake, setTestingIntake] = useState(false);
  const [testError, setTestError] = useState<string | null>(null);
  const [testLeadId, setTestLeadId] = useState<string | null>(null);
  const apiBase = useMemo(() => getPublicApiBaseUrl(), []);
  const webhookUrl = useMemo(
    () => buildVoiceWebhookUrl(apiBase),
    [apiBase],
  );
  const messageUrl = useMemo(
    () => buildVoiceMessageUrl(apiBase),
    [apiBase],
  );

  const handleCopy = useCallback(
    async (value: string) => {
      try {
        await navigator.clipboard.writeText(value);
        setCopyMessage(t("copied"));
      } catch {
        setCopyMessage(t("copyFailed"));
      }
      window.setTimeout(() => setCopyMessage(null), 2500);
    },
    [t],
  );

  async function handleTestVoiceIntake() {
    setTestingIntake(true);
    setTestError(null);
    setTestLeadId(null);
    try {
      const result = await sendTestVoiceIntake();
      setTestLeadId(result.lead_id);
    } catch (err) {
      setTestError(
        formatUserFacingError(err, t("voiceTestIntakeFailed"), errorMessages),
      );
    } finally {
      setTestingIntake(false);
    }
  }

  return (
    <details className="card voice-setup-disclosure">
      <summary className="voice-setup-disclosure-summary">
        <span className="voice-setup-disclosure-title">
          {t("voiceIntakeDisclosureTitle")}
        </span>
        <span className="muted voice-setup-disclosure-hint">
          {t("voiceIntakeDisclosureHint")}
        </span>
      </summary>

      <section className="stack voice-setup-disclosure-body" aria-labelledby="voice-setup-title">
        <div className="stack">
          <h2 id="voice-setup-title" className="page-title">
            {t("voiceIntakeTitle")}
          </h2>
          <p className="muted">{t("voiceIntakeDescription")}</p>
        </div>

        <div className="voice-test-intake-block stack">
          <p className="muted">{t("voiceTestIntakeHint")}</p>
          <button
            type="button"
            className="button secondary"
            onClick={() => void handleTestVoiceIntake()}
            disabled={testingIntake}
          >
            {testingIntake ? t("voiceTestIntakeRunning") : t("voiceTestIntake")}
          </button>
          {testError ? <AlertBanner variant="error">{testError}</AlertBanner> : null}
          {testLeadId ? (
            <AlertBanner variant="success">
              {t("voiceTestIntakeSuccess")}{" "}
              <Link href={`/leads/${testLeadId}`}>{t("voiceTestIntakeViewInbox")}</Link>
            </AlertBanner>
          ) : null}
        </div>

        <div className="stack">
          <p className="muted">{t("voiceIntakeSlugHint", { slug: companySlug })}</p>
          <label className="field">
            <span>{t("voiceWebhookUrl")}</span>
            <div className="field-with-action">
              <input readOnly value={webhookUrl} aria-readonly="true" />
              <button
                type="button"
                className="button secondary"
                onClick={() => void handleCopy(webhookUrl)}
              >
                {t("copySnippet")}
              </button>
            </div>
          </label>
          <label className="field">
            <span>{t("voiceMessageUrl")}</span>
            <div className="field-with-action">
              <input readOnly value={messageUrl} aria-readonly="true" />
              <button
                type="button"
                className="button secondary"
                onClick={() => void handleCopy(messageUrl)}
              >
                {t("copySnippet")}
              </button>
            </div>
          </label>
          <p className="muted field-hint">{t("voiceWebhookSecretHint")}</p>
          {copyMessage ? (
            <p className="muted" role="status" aria-live="polite">
              {copyMessage}
            </p>
          ) : null}
        </div>

        <ol className="voice-setup-steps">
          <li>{t("voiceSetupStepVapi")}</li>
          <li>{t("voiceSetupStepTwilio")}</li>
          <li>{t("voiceSetupStepMetadata", { slug: companySlug })}</li>
          <li>{t("voiceSetupStepModels")}</li>
          <li>{t("voiceSetupStepTool")}</li>
          <li>{t("voiceSetupStepSecret")}</li>
        </ol>

        <p className="muted field-hint">{t("voiceSetupDocsHint")}</p>
      </section>
    </details>
  );
}
