"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { sendLeadMessage } from "@/lib/api";
import { scrollChatContainerToBottom } from "@/lib/chat-scroll";
import {
  COMPANY_SETTINGS_CACHE_KEY,
  getDashboardCache,
  loadCachedCompanySettings,
} from "@/lib/dashboard-cache";
import {
  getDemoChatExampleKeys,
  getDemoChatExampleMessage,
  type TradeDemoChatExampleKey,
} from "@/lib/demo-chat-examples";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import { Link } from "@/i18n/navigation";
import { translateWithTradeOverride } from "@/lib/trade-copy";
import { tradeNamespace } from "@/lib/trades/types";
import type { CompanySettings } from "@/lib/types";

export function createDemoChatConversationId(): string {
  return `demo-chat-${Date.now()}`;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

function createConversationId(): string {
  return createDemoChatConversationId();
}

function createMessageId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function DemoChat() {
  const { company, loading: authLoading, error: authError } = useAuth();
  const [settings, setSettings] = useState<CompanySettings | null>(() =>
    getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
  );
  const trade = settings?.trade ?? null;
  const t = useTranslations("demoChat");
  const tTrade = useTranslations(tradeNamespace(trade, "demoChat"));
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const tt = (key: string) =>
    translateWithTradeOverride(t, tTrade, key, Boolean(trade));
  const examplePromptKeys = useMemo(
    () => getDemoChatExampleKeys(trade),
    [trade],
  );
  const [conversationId, setConversationId] = useState(createDemoChatConversationId);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [leadComplete, setLeadComplete] = useState(false);
  const [leadId, setLeadId] = useState<string | null>(null);
  const [hasOpenFields, setHasOpenFields] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    void loadCachedCompanySettings(setSettings);
  }, []);

  const assistantLabel = company?.name?.trim() || t("assistant");
  const showExampleChips =
    messages.length === 0 && !loading && !leadComplete && !authLoading;

  useEffect(() => {
    if (messages.length === 0) {
      return;
    }

    scrollChatContainerToBottom(messagesContainerRef.current);
  }, [messages, loading, leadComplete]);

  function handleNewConversation() {
    setConversationId(createConversationId());
    setMessages([]);
    setInput("");
    setError(null);
    setLeadComplete(false);
    setLeadId(null);
    setHasOpenFields(false);
  }

  async function sendMessage(message: string) {
    const trimmed = message.trim();
    if (!trimmed || loading || leadComplete || authLoading) {
      return;
    }

    setError(null);
    setMessages((current) => [
      ...current,
      { id: createMessageId(), role: "user", content: trimmed },
    ]);
    setLoading(true);

    try {
      const response = await sendLeadMessage({
        conversation_id: conversationId,
        message: trimmed,
      });

      setMessages((current) => [
        ...current,
        { id: createMessageId(), role: "assistant", content: response.reply },
      ]);
      setHasOpenFields((response.missing_fields ?? []).length > 0);

      if (response.lead_complete) {
        setLeadComplete(true);
        setLeadId(response.lead_id);
        setHasOpenFields(false);
      }
    } catch (err) {
      setError(formatUserFacingError(err, t("sendFailed"), errorMessages));
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = input.trim();
    if (!message) {
      return;
    }

    setInput("");
    await sendMessage(message);
  }

  function handleExamplePrompt(key: TradeDemoChatExampleKey) {
    try {
      const message = getDemoChatExampleMessage(
        (messageKey) => tt(messageKey),
        key,
      );
      void sendMessage(message);
    } catch {
      setError(t("examplePromptFailed"));
    }
  }

  return (
    <div className="stack">
      <PageHeader title={tt("title")} description={tt("description")}>
        <button
          type="button"
          className="button secondary"
          onClick={handleNewConversation}
          disabled={loading}
        >
          {t("newConversation")}
        </button>
      </PageHeader>

      <AlertBanner variant="info">{t("sandboxNotice")}</AlertBanner>

      {authError ? <AlertBanner>{authError}</AlertBanner> : null}

      {authLoading ? <LoadingState label={t("loadingAccount")} /> : null}

      <div className="chat-panel card">
        <div className="chat-messages" ref={messagesContainerRef} aria-live="polite">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <h3 className="chat-empty-title">{t("welcomeTitle")}</h3>
              <p>{tt("welcomeBody")}</p>
              {showExampleChips ? (
                <>
                  <p className="chat-prompts-label">{t("examplePromptsLabel")}</p>
                  <div className="chat-prompt-chips">
                    {examplePromptKeys.map((key) => (
                      <button
                        key={key}
                        type="button"
                        className="button secondary"
                        disabled={loading || authLoading}
                        onClick={() => handleExamplePrompt(key)}
                      >
                        {tt(`examplePrompts.${key}`)}
                      </button>
                    ))}
                  </div>
                </>
              ) : null}
            </div>
          ) : null}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`chat-message chat-message-${message.role}`}
            >
              <span className="chat-message-label">
                {message.role === "user" ? t("customer") : assistantLabel}
              </span>
              <p>{message.content}</p>
            </div>
          ))}

          {loading ? (
            <div className="chat-message chat-message-assistant">
              <span className="chat-message-label">{assistantLabel}</span>
              <p className="muted">{t("thinking")}</p>
            </div>
          ) : null}
        </div>

        {error ? <AlertBanner>{error}</AlertBanner> : null}

        {leadComplete && leadId ? (
          <div className="chat-success-panel">
            <h3 className="chat-success-title">{t("successTitle")}</h3>
            <p className="muted">{tt("successBody")}</p>
            <div className="chat-success-actions">
              <Link href={`/leads/${leadId}`} className="button">
                {t("viewLead")}
              </Link>
              <button
                type="button"
                className="button secondary"
                onClick={handleNewConversation}
              >
                {t("tryAnother")}
              </button>
            </div>
          </div>
        ) : null}

        {!leadComplete && hasOpenFields ? (
          <p className="muted chat-hint">{t("progressHint")}</p>
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
