"use client";

import { useTranslations } from "next-intl";

import { INQUIRY_SOURCE_BADGE_CLASS } from "@/lib/inquiry-source";
import type { LeadSource } from "@/lib/types";

interface InquirySourceBadgeProps {
  source: LeadSource;
}

export function InquirySourceBadge({ source }: InquirySourceBadgeProps) {
  const t = useTranslations("leads");

  return (
    <span className={`badge ${INQUIRY_SOURCE_BADGE_CLASS[source]}`}>
      {source === "website" ? t("sourceWebsite") : t("sourceTest")}
    </span>
  );
}
