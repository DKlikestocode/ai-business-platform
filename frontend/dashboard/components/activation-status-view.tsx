"use client";

import { useTranslations } from "next-intl";

import {
  activationStatusClassName,
  formatActivationTimestamp,
} from "@/lib/activation-display";
import type { CompanyActivation } from "@/lib/types";

interface ActivationStatusViewProps {
  activation: CompanyActivation;
  locale: string;
}

export function ActivationStatusView({
  activation,
  locale,
}: ActivationStatusViewProps) {
  const t = useTranslations("activation");
  const lastSeen = formatActivationTimestamp(
    activation.widget_last_seen_at,
    locale,
  );
  const showMeta =
    activation.status === "live" || activation.status === "stale";

  return (
    <div className={activationStatusClassName(activation.status)}>
      <p className="activation-status-message">
        {t(`status.${activation.status}`)}
      </p>
      {showMeta ? (
        <div className="activation-status-meta">
          {activation.widget_last_origin ? (
            <p className="muted">
              {t("lastOrigin", {
                origin: activation.widget_last_origin,
              })}
            </p>
          ) : null}
          {lastSeen ? (
            <p className="muted">{t("lastSeen", { date: lastSeen })}</p>
          ) : null}
        </div>
      ) : null}
      {activation.status === "stale" ? (
        <p className="muted activation-stale-guidance">{t("staleGuidance")}</p>
      ) : null}
    </div>
  );
}

export function activationRefreshLabel(
  status: CompanyActivation["status"] | null | undefined,
  labels: { refresh: string; refreshStale: string },
): string {
  return status === "stale" ? labels.refreshStale : labels.refresh;
}
