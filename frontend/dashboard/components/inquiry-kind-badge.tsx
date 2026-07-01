"use client";

import { useTranslations } from "next-intl";

import {
  INQUIRY_KIND_BADGE_CLASS,
  INQUIRY_KIND_LABEL_KEY,
  normalizeInquiryKind,
} from "@/lib/inquiry-kind";
import type { Lead } from "@/lib/types";

interface InquiryKindBadgeProps {
  inquiryKind: Lead["inquiry_kind"];
}

export function InquiryKindBadge({ inquiryKind }: InquiryKindBadgeProps) {
  const t = useTranslations("leads");
  const resolvedKind = normalizeInquiryKind(inquiryKind);
  const badgeClass = INQUIRY_KIND_BADGE_CLASS[resolvedKind];

  return (
    <span className={`badge ${badgeClass}`}>
      {t(INQUIRY_KIND_LABEL_KEY[resolvedKind])}
    </span>
  );
}
