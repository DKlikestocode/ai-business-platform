"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";

import {
  buildVoiceMessageUrl,
  buildVoiceWebhookUrl,
} from "@/lib/voice-setup";

interface VoiceSetupPanelProps {
  companySlug: string;
}

export function VoiceSetupPanel({ companySlug }: VoiceSetupPanelProps) {
  const t = useTranslations("settings");
  const origin = typeof window !== "undefined" ? window.location.origin : "";
  const webhookUrl = useMemo(() => buildVoiceWebhookUrl(origin), [origin]);
  const messageUrl = useMemo(() => buildVoiceMessageUrl(origin), [origin]);

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
          <input readOnly value={webhookUrl} aria-readonly="true" />
        </label>
        <label className="field">
          <span>{t("voiceMessageUrl")}</span>
          <input readOnly value={messageUrl} aria-readonly="true" />
        </label>
      </div>

      <ol className="voice-setup-steps">
        <li>{t("voiceSetupStepVapi")}</li>
        <li>{t("voiceSetupStepTwilio")}</li>
        <li>{t("voiceSetupStepMetadata", { slug: companySlug })}</li>
        <li>{t("voiceSetupStepModels")}</li>
        <li>{t("voiceSetupStepTool")}</li>
      </ol>

      <p className="muted field-hint">{t("voiceSetupDocsHint")}</p>
    </section>
  );
}
