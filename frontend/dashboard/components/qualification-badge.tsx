"use client";

import { useTranslations } from "next-intl";

import { QUALIFICATION_BADGE_CLASS } from "@/lib/lead-qualification";
import type { QualificationStatus } from "@/lib/types";

interface QualificationBadgeProps {
  status: QualificationStatus;
}

export function QualificationBadge({ status }: QualificationBadgeProps) {
  const t = useTranslations("qualification");

  return (
    <span className={`badge ${QUALIFICATION_BADGE_CLASS[status]}`}>
      {t(status)}
    </span>
  );
}
