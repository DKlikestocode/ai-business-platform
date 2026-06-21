"use client";

import { useLocale, useTranslations } from "next-intl";

import {
  formatInquiryNotificationTimestamp,
  isInquiryNotificationSent,
} from "@/lib/inquiry-notification";

interface InquiryNotificationIndicatorProps {
  notificationSentAt: string | null;
  variant?: "card" | "detail";
}

export function InquiryNotificationIndicator({
  notificationSentAt,
  variant = "card",
}: InquiryNotificationIndicatorProps) {
  const locale = useLocale();
  const t = useTranslations(variant === "detail" ? "leadDetail" : "leads");
  const sent = isInquiryNotificationSent(notificationSentAt);
  const sentAtLabel = formatInquiryNotificationTimestamp(
    notificationSentAt,
    locale,
    variant === "detail" ? "full" : "medium",
  );

  if (variant === "detail") {
    return (
      <p
        className="inquiry-notification-indicator inquiry-notification-detail"
        role="status"
      >
        {sent && sentAtLabel
          ? t("notificationSentDetail", { date: sentAtLabel })
          : t("notificationNotSentDetail")}
      </p>
    );
  }

  return (
    <p className="inquiry-notification-indicator" role="status">
      <span
        className={
          sent
            ? "inquiry-notification-sent"
            : "inquiry-notification-not-sent"
        }
      >
        {sent ? t("notificationSentShort") : t("notificationNotSentShort")}
      </span>
      {sent && sentAtLabel ? (
        <span className="inquiry-notification-time muted">
          {" "}
          · {sentAtLabel}
        </span>
      ) : null}
    </p>
  );
}
