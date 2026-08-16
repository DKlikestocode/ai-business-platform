"use client";

import { useTranslations } from "next-intl";

import type { IntakeStatus } from "@/lib/types";

export function IntakeStatusBadge({ status }: { status: IntakeStatus }) {
  const t = useTranslations("intake.statuses");

  return (
    <span className={`intake-status-badge intake-status-${status}`}>
      {t(status)}
    </span>
  );
}
