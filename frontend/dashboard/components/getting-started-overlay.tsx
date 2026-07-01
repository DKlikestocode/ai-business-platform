"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  CLOSE_GETTING_STARTED_EVENT,
  OPEN_GETTING_STARTED_EVENT,
} from "@/lib/getting-started-overlay";

const AUTO_OPEN_SESSION_KEY = "getting-started-overlay-auto-opened";

interface GettingStartedOverlayProps {
  visible: boolean;
  autoOpen: boolean;
  title: string;
  subtitle: string;
  closeLabel: string;
  launcherLabel: string;
  progressLabel: string;
  children: ReactNode;
}

export function GettingStartedOverlay({
  visible,
  autoOpen,
  title,
  subtitle,
  closeLabel,
  launcherLabel,
  progressLabel,
  children,
}: GettingStartedOverlayProps) {
  const [open, setOpen] = useState(false);

  const openPanel = useCallback(() => setOpen(true), []);
  const closePanel = useCallback(() => setOpen(false), []);

  useEffect(() => {
    const onOpen = () => openPanel();
    const onClose = () => closePanel();
    window.addEventListener(OPEN_GETTING_STARTED_EVENT, onOpen);
    window.addEventListener(CLOSE_GETTING_STARTED_EVENT, onClose);
    return () => {
      window.removeEventListener(OPEN_GETTING_STARTED_EVENT, onOpen);
      window.removeEventListener(CLOSE_GETTING_STARTED_EVENT, onClose);
    };
  }, [closePanel, openPanel]);

  useEffect(() => {
    if (!visible || !autoOpen) {
      return;
    }
    if (sessionStorage.getItem(AUTO_OPEN_SESSION_KEY) === "1") {
      return;
    }
    sessionStorage.setItem(AUTO_OPEN_SESSION_KEY, "1");
    openPanel();
  }, [autoOpen, openPanel, visible]);

  useEffect(() => {
    if (!open) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        closePanel();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [closePanel, open]);

  useEffect(() => {
    if (!visible) {
      setOpen(false);
    }
  }, [visible]);

  const launcherAria = useMemo(
    () => `${launcherLabel} — ${progressLabel}`,
    [launcherLabel, progressLabel],
  );

  if (!visible) {
    return null;
  }

  return (
    <>
      <div
        className={`getting-started-overlay-panel${open ? " is-open" : ""}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        aria-hidden={!open}
      >
        <div className="getting-started-overlay-header">
          <div className="getting-started-overlay-heading">
            <strong>{title}</strong>
            <span className="getting-started-overlay-subtitle">{subtitle}</span>
            <span className="getting-started-overlay-progress">{progressLabel}</span>
          </div>
          <button
            type="button"
            className="getting-started-overlay-close"
            onClick={closePanel}
            aria-label={closeLabel}
          >
            ×
          </button>
        </div>
        <div className="getting-started-overlay-body">{children}</div>
      </div>

      {!open ? (
        <button
          type="button"
          className="getting-started-overlay-launcher"
          onClick={openPanel}
          aria-label={launcherAria}
        >
          <SetupIcon />
          <span className="getting-started-overlay-launcher-label">
            {launcherLabel}
          </span>
        </button>
      ) : null}
    </>
  );
}

function SetupIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M9 11l3 3L22 4"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
