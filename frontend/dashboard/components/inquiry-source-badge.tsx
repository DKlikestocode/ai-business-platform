"use client";

import { useTranslations } from "next-intl";

import { INQUIRY_SOURCE_LABEL_KEY } from "@/lib/inquiry-handoff";
import { INQUIRY_SOURCE_BADGE_CLASS } from "@/lib/inquiry-source";
import type { LeadSource } from "@/lib/types";

interface InquirySourceBadgeProps {
  source: LeadSource;
}

export function InquirySourceBadge({ source }: InquirySourceBadgeProps) {
  const t = useTranslations("leads");
  const resolvedSource: LeadSource = source === "test" ? "test" : "website";
  const badgeClass =
    INQUIRY_SOURCE_BADGE_CLASS[resolvedSource] ??
    INQUIRY_SOURCE_BADGE_CLASS.website;

  return (
    <span className={`badge ${badgeClass}`}>
      {t(INQUIRY_SOURCE_LABEL_KEY[resolvedSource])}
    </span>
  );
}
