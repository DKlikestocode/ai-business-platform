"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { sendLeadMessage } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { markOnboardingStepComplete } from "@/lib/onboarding";
import type { LeadExtractedData } from "@/lib/types";

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
      setError(formatUserFacingError(err, "Failed to send message."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <PageHeader
        title="Demo Chat"
        description="Test the lead capture agent before or after installing the website widget."
      >
        <button
          type="button"
          className="button secondary"
          onClick={handleNewConversation}
          disabled={loading}
        >
          New conversation
        </button>
      </PageHeader>

      <p className="muted">
        Conversation ID: <code>{conversationId}</code>
      </p>

      {authError ? <AlertBanner>{authError}</AlertBanner> : null}

      {authLoading ? <LoadingState label="Loading account..." /> : null}

      <div className="chat-panel card">
        <div className="chat-messages" aria-live="polite">
          {messages.length === 0 ? (
            <div className="chat-empty">
              Start a conversation as a customer inquiry. The Lead Agent will
              ask for details like name, phone, location, and service needed.
            </div>
          ) : null}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`chat-message chat-message-${message.role}`}
            >
              <span className="chat-message-label">
                {message.role === "user" ? "You" : "Lead Agent"}
              </span>
              <p>{message.content}</p>
            </div>
          ))}

          {loading ? (
            <div className="chat-message chat-message-assistant">
              <span className="chat-message-label">Lead Agent</span>
              <p className="muted">Thinking...</p>
            </div>
          ) : null}

          <div ref={messagesEndRef} />
        </div>

        {error ? <AlertBanner>{error}</AlertBanner> : null}

        {leadComplete && leadId ? (
          <div className="notice chat-success">
            Lead captured successfully.{" "}
            <Link href={`/leads/${leadId}`} className="link">
              View lead details
            </Link>
          </div>
        ) : null}

        {!leadComplete && missingFields.length > 0 ? (
          <p className="muted chat-hint">
            Still needed: {formatMissingFields(missingFields)}
          </p>
        ) : null}

        {!leadComplete && extractedData?.name ? (
          <p className="muted chat-hint">
            Captured so far: {extractedData.name}
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
                ? "Lead complete. Start a new conversation to continue."
                : "Type your message..."
            }
            disabled={loading || leadComplete || authLoading}
            onChange={(event) => setInput(event.target.value)}
          />
          <button
            type="submit"
            className="button"
            disabled={loading || leadComplete || authLoading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
