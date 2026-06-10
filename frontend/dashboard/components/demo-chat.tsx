"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { sendLeadMessage } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import { markOnboardingStepComplete } from "@/lib/onboarding";
import type { LeadExtractedData } from "@/lib/types";
import { Link } from "@/i18n/navigation";

const DEFAULT_CONVERSATION_ID = "demo-chat-001";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

function createConversationId(): string {
  return `demo-chat-${Date.now()}`;
}

function createMessageId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function formatMissingFields(fields: string[]): string {
  if (fields.length === 0) {
    return "";
  }
  return fields.join(", ");
}

export function DemoChat() {
  const { company, loading: authLoading, error: authError } = useAuth();
  const t = useTranslations("demoChat");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const [conversationId, setConversationId] = useState(DEFAULT_CONVERSATION_ID);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [leadComplete, setLeadComplete] = useState(false);
  const [leadId, setLeadId] = useState<string | null>(null);
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [extractedData, setExtractedData] = useState<LeadExtractedData | null>(
    null,
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, leadComplete]);

  function handleNewConversation() {
    setConversationId(createConversationId());
    setMessages([]);
    setInput("");
    setError(null);
    setLeadComplete(false);
    setLeadId(null);
    setMissingFields([]);
    setExtractedData(null);
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = input.trim();
    if (!message || loading || leadComplete || authLoading) {
      return;
    }

    setInput("");
    setError(null);
    setMessages((current) => [
      ...current,
      { id: createMessageId(), role: "user", content: message },
    ]);
    setLoading(true);

    try {
      const response = await sendLeadMessage({
        conversation_id: conversationId,
        message,
      });

      setMessages((current) => [
        ...current,
        { id: createMessageId(), role: "assistant", content: response.reply },
      ]);
      setMissingFields(response.missing_fields);
      setExtractedData(response.extracted_data);

      if (company) {
        markOnboardingStepComplete(company.id, "test_widget");
      }

      if (response.lead_complete) {
        setLeadComplete(true);
        setLeadId(response.lead_id);
      }
    } catch (err) {
      setError(formatUserFacingError(err, t("sendFailed"), errorMessages));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <PageHeader title={t("title")} description={t("description")}>
        <button
          type="button"
          className="button secondary"
          onClick={handleNewConversation}
          disabled={loading}
        >
          {t("newConversation")}
        </button>
      </PageHeader>

      <p className="muted">
        {t("conversationId")} <code>{conversationId}</code>
      </p>

      {authError ? <AlertBanner>{authError}</AlertBanner> : null}

      {authLoading ? <LoadingState label={t("loadingAccount")} /> : null}

      <div className="chat-panel card">
        <div className="chat-messages" aria-live="polite">
          {messages.length === 0 ? (
            <div className="chat-empty">{t("emptyState")}</div>
          ) : null}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`chat-message chat-message-${message.role}`}
            >
              <span className="chat-message-label">
                {message.role === "user" ? t("you") : t("leadAgent")}
              </span>
              <p>{message.content}</p>
            </div>
          ))}

          {loading ? (
            <div className="chat-message chat-message-assistant">
              <span className="chat-message-label">{t("leadAgent")}</span>
              <p className="muted">{t("thinking")}</p>
            </div>
          ) : null}

          <div ref={messagesEndRef} />
        </div>

        {error ? <AlertBanner>{error}</AlertBanner> : null}

        {leadComplete && leadId ? (
          <div className="notice chat-success">
            {t("leadCaptured")}{" "}
            <Link href={`/leads/${leadId}`} className="link">
              {t("viewLead")}
            </Link>
          </div>
        ) : null}

        {!leadComplete && missingFields.length > 0 ? (
          <p className="muted chat-hint">
            {t("stillNeeded")} {formatMissingFields(missingFields)}
          </p>
        ) : null}

        {!leadComplete && extractedData?.name ? (
          <p className="muted chat-hint">
            {t("capturedSoFar")} {extractedData.name}
            {extractedData.phone ? ` · ${extractedData.phone}` : ""}
            {extractedData.location ? ` · ${extractedData.location}` : ""}
          </p>
        ) : null}

        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            className="input"
            type="text"
            value={input}
            placeholder={
              leadComplete
                ? t("placeholderComplete")
                : t("placeholderMessage")
            }
            disabled={loading || leadComplete || authLoading}
            onChange={(event) => setInput(event.target.value)}
          />
          <button
            type="submit"
            className="button"
            disabled={loading || leadComplete || authLoading || !input.trim()}
          >
            {tCommon("send")}
          </button>
        </form>
      </div>
    </div>
  );
}
