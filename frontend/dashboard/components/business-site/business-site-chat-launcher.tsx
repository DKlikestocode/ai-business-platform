"use client";

import {
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";

const OPEN_CHAT_EVENT = "business-site:open-chat";

export function openBusinessSiteChat() {
  window.dispatchEvent(new Event(OPEN_CHAT_EVENT));
}

interface BusinessSiteChatLauncherProps {
  title: string;
  closeLabel: string;
  launcherLabel: string;
  children: ReactNode;
}

export function BusinessSiteChatLauncher({
  title,
  closeLabel,
  launcherLabel,
  children,
}: BusinessSiteChatLauncherProps) {
  const [open, setOpen] = useState(false);

  const openChat = useCallback(() => setOpen(true), []);
  const closeChat = useCallback(() => setOpen(false), []);

  useEffect(() => {
    const onOpen = () => openChat();
    window.addEventListener(OPEN_CHAT_EVENT, onOpen);
    return () => window.removeEventListener(OPEN_CHAT_EVENT, onOpen);
  }, [openChat]);

  useEffect(() => {
    if (window.location.hash === "#anfrage") {
      openChat();
    }
    const onHashChange = () => {
      if (window.location.hash === "#anfrage") {
        openChat();
      }
    };
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, [openChat]);

  useEffect(() => {
    if (!open) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        closeChat();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, closeChat]);

  return (
    <>
      <div
        className={`business-site-chat-panel${open ? " is-open" : ""}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        aria-hidden={!open}
      >
        <div className="business-site-chat-panel-header">
          <strong>{title}</strong>
          <button
            type="button"
            className="business-site-chat-panel-close"
            onClick={closeChat}
            aria-label={closeLabel}
          >
            ×
          </button>
        </div>
        <div className="business-site-chat-panel-body">{children}</div>
      </div>

      {!open ? (
        <button
          type="button"
          className="business-site-chat-launcher"
          onClick={openChat}
          aria-label={launcherLabel}
        >
          <ChatIcon />
          <span className="business-site-chat-launcher-label">{title}</span>
        </button>
      ) : null}
    </>
  );
}

function ChatIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
