"use client";

import { useLocale, useTranslations } from "next-intl";

import {
  formatInquiryContactedTimestamp,
  isInquiryContacted,
} from "@/lib/inquiry-contacted";

interface InquiryContactedIndicatorProps {
  contactedAt: string | null;
  variant?: "card" | "detail";
}

export function InquiryContactedIndicator({
  contactedAt,
  variant = "card",
}: InquiryContactedIndicatorProps) {
  const locale = useLocale();
  const t = useTranslations(variant === "detail" ? "leadDetail" : "leads");
  const contacted = isInquiryContacted(contactedAt);
  const contactedAtLabel = formatInquiryContactedTimestamp(
    contactedAt,
    locale,
    variant === "detail" ? "full" : "medium",
  );

  if (!contacted || !contactedAtLabel) {
    return null;
  }

  if (variant === "detail") {
    return (
      <p
        className="inquiry-contacted-indicator inquiry-contacted-detail"
        role="status"
      >
        {t("contactedAtDetail", { date: contactedAtLabel })}
      </p>
    );
  }

  return (
    <p className="inquiry-contacted-indicator" role="status">
      <span className="inquiry-contacted-label">{t("contactedAtShort")}</span>
      <span className="inquiry-contacted-time muted"> · {contactedAtLabel}</span>
    </p>
  );
}
