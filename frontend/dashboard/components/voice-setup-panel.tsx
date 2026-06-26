"use client";

import { useCallback, useMemo, useState } from "react";
import { useTranslations } from "next-intl";

import {
  buildVoiceMessageUrl,
  buildVoiceWebhookUrl,
} from "@/lib/voice-setup";
import { getPublicApiBaseUrl } from "@/lib/widget-embed";

interface VoiceSetupPanelProps {
  companySlug: string;
}

export function VoiceSetupPanel({ companySlug }: VoiceSetupPanelProps) {
  const t = useTranslations("settings");
  const [copyMessage, setCopyMessage] = useState<string | null>(null);
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

  return (
    <section className="card stack" aria-labelledby="voice-setup-title">
      <div className="stack">
        <h2 id="voice-setup-title" className="page-title">
          {t("voiceIntakeTitle")}
        </h2>
        <p className="muted">{t("voiceIntakeDescription")}</p>
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
  );
}
