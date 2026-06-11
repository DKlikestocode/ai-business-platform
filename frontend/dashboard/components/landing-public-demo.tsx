"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

import { Link } from "@/i18n/navigation";

const DEMO_SCENARIO_KEYS = ["plumber", "roofer", "electrician"] as const;

type DemoScenarioKey = (typeof DEMO_SCENARIO_KEYS)[number];

export function LandingPublicDemo() {
  const t = useTranslations("landing.publicDemo");
  const [selectedScenario, setSelectedScenario] = useState<DemoScenarioKey | null>(
    null,
  );

  function handleReset() {
    setSelectedScenario(null);
  }

  return (
    <section
      className="public-demo shell"
      aria-labelledby="public-demo-title"
    >
      <div className="public-demo-layout">
        <div className="public-demo-copy">
          <h2 id="public-demo-title" className="public-demo-title">
            {t("title")}
          </h2>
          <p className="public-demo-lead muted">{t("lead")}</p>
          <p className="public-demo-disclaimer">{t("disclaimer")}</p>

          <p className="chat-prompts-label">{t("chipsLabel")}</p>
          <div className="chat-prompt-chips">
            {DEMO_SCENARIO_KEYS.map((key) => (
              <button
                key={key}
                type="button"
                className="button secondary"
                aria-pressed={selectedScenario === key}
                onClick={() => setSelectedScenario(key)}
              >
                {t(`chips.${key}`)}
              </button>
            ))}
          </div>

          {selectedScenario ? (
            <div className="public-demo-actions">
              <Link href="/onboarding" className="button">
                {t("startCta")}
              </Link>
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

        <div className="chat-panel card public-demo-chat">
          <div className="chat-messages" aria-live="polite">
            {selectedScenario ? (
              <>
                <div className="chat-message chat-message-user">
                  <span className="chat-message-label">{t("customerLabel")}</span>
                  <p>{t(`scenarios.${selectedScenario}.customer`)}</p>
                </div>
                <div className="chat-message chat-message-assistant">
                  <span className="chat-message-label">
                    {t("assistantLabel")}
                  </span>
                  <p>{t(`scenarios.${selectedScenario}.assistant1`)}</p>
                </div>
                <div className="chat-message chat-message-assistant">
                  <span className="chat-message-label">
                    {t("assistantLabel")}
                  </span>
                  <p>{t(`scenarios.${selectedScenario}.assistant2`)}</p>
                </div>
              </>
            ) : (
              <div className="chat-empty">
                <p>{t("emptyState")}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
