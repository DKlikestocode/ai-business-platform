"use client";

import { useLocale, useTranslations } from "next-intl";

import {
  formatCustomerConfirmationTimestamp,
  isCustomerConfirmationSent,
} from "@/lib/inquiry-customer-confirmation";

interface InquiryCustomerConfirmationIndicatorProps {
  customerConfirmationSentAt: string | null;
  variant?: "card" | "detail";
}

export function InquiryCustomerConfirmationIndicator({
  customerConfirmationSentAt,
  variant = "card",
}: InquiryCustomerConfirmationIndicatorProps) {
  const locale = useLocale();
  const t = useTranslations(variant === "detail" ? "leadDetail" : "leads");
  const sent = isCustomerConfirmationSent(customerConfirmationSentAt);
  const sentAtLabel = formatCustomerConfirmationTimestamp(
    customerConfirmationSentAt,
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
          ? t("customerConfirmationSentDetail", { date: sentAtLabel })
          : t("customerConfirmationNotSentDetail")}
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
        {sent
          ? t("customerConfirmationSentShort")
          : t("customerConfirmationNotSentShort")}
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
