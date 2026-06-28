"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";

import { PilotBookingLink } from "@/components/pilot-booking-link";
import {
  LandingDemoApiError,
  createLandingDemoConversationId,
  isLandingDemoLimitStatus,
  sendLandingDemoMessage,
} from "@/lib/landing-demo";
import { scrollChatContainerToBottom } from "@/lib/chat-scroll";

const STARTER_KEYS = ["plumber", "roofer", "electrician"] as const;

type StarterKey = (typeof STARTER_KEYS)[number];

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

function createMessageId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function LandingPublicDemo() {
  const t = useTranslations("landing.publicDemo");
  const tCommon = useTranslations("common");
  const [conversationId, setConversationId] = useState(createLandingDemoConversationId);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limitReached, setLimitReached] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const showStarters = messages.length === 0 && !loading && !limitReached;

  useEffect(() => {
    if (messages.length === 0) {
      return;
    }

    scrollChatContainerToBottom(messagesContainerRef.current);
  }, [messages, loading, limitReached]);

  function handleReset() {
    setConversationId(createLandingDemoConversationId());
    setMessages([]);
    setInput("");
    setError(null);
    setLimitReached(false);
  }

  async function sendMessage(message: string) {
    const trimmed = message.trim();
    if (!trimmed || loading || limitReached) {
      return;
    }

    setError(null);
    setMessages((current) => [
      ...current,
      { id: createMessageId(), role: "user", content: trimmed },
    ]);
    setLoading(true);

    try {
      const response = await sendLandingDemoMessage({
        conversation_id: conversationId,
        message: trimmed,
      });

      setMessages((current) => [
        ...current,
        { id: createMessageId(), role: "assistant", content: response.reply },
      ]);
    } catch (err) {
      if (err instanceof LandingDemoApiError && isLandingDemoLimitStatus(err.status)) {
        setLimitReached(true);
      } else {
        setError(err instanceof Error ? err.message : t("sendFailed"));
      }
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

  function handleStarter(key: StarterKey) {
    void sendMessage(t(`starters.${key}`));
  }

  return (
    <section
      id="live-demo"
      className="landing-section public-demo shell"
      aria-labelledby="public-demo-title"
    >
      <div className="public-demo-frame card">
        <div className="public-demo-layout">
          <div className="public-demo-copy">
            <p className="eyebrow">{t("eyebrow")}</p>
            <h2 id="public-demo-title" className="landing-section-title">
              {t("title")}
            </h2>
            <p className="landing-section-lead muted">{t("lead")}</p>
            <p className="public-demo-disclaimer">{t("disclaimer")}</p>

          {showStarters ? (
            <>
              <p className="chat-prompts-label">{t("chipsLabel")}</p>
              <div className="chat-prompt-chips">
                {STARTER_KEYS.map((key) => (
                  <button
                    key={key}
                    type="button"
                    className="button secondary"
                    disabled={loading}
                    onClick={() => handleStarter(key)}
                  >
                    {t(`chips.${key}`)}
                  </button>
                ))}
              </div>
            </>
          ) : null}

          {messages.length > 0 || limitReached ? (
            <div className="public-demo-actions">
              <PilotBookingLink className="button">
                {t("startCta")}
              </PilotBookingLink>
              <button
                type="button"
                className="button secondary"
                onClick={handleReset}
              >
                {t("resetCta")}
              </button>
            </div>
          ) : null}
        </div>

        <div className="chat-panel public-demo-chat">
          <div className="chat-messages" ref={messagesContainerRef} aria-live="polite">
            {messages.length === 0 && !loading ? (
              <div className="chat-empty">
                <p>{t("emptyState")}</p>
              </div>
            ) : null}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`chat-message chat-message-${message.role}`}
              >
                <span className="chat-message-label">
                  {message.role === "user"
                    ? t("customerLabel")
                    : t("assistantLabel")}
                </span>
                <p>{message.content}</p>
              </div>
            ))}

            {loading ? (
              <div className="chat-message chat-message-assistant">
                <span className="chat-message-label">{t("assistantLabel")}</span>
                <p className="muted">{t("thinking")}</p>
              </div>
            ) : null}

            {limitReached ? (
              <div className="chat-message chat-message-assistant">
                <span className="chat-message-label">{t("assistantLabel")}</span>
                <p>{t("limitReached")}</p>
              </div>
            ) : null}
          </div>

          {error ? <p className="alert">{error}</p> : null}

          <form className="chat-form" onSubmit={handleSubmit}>
            <input
              className="input"
              type="text"
              value={input}
              placeholder={
                limitReached ? t("placeholderLimit") : t("placeholderMessage")
              }
              disabled={loading || limitReached}
              onChange={(event) => setInput(event.target.value)}
            />
            <button
              type="submit"
              className="button"
              disabled={loading || limitReached || !input.trim()}
            >
              {tCommon("send")}
            </button>
          </form>
        </div>
        </div>
      </div>
    </section>
  );
}
