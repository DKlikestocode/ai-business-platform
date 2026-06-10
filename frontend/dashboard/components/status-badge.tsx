"use client";

import { useTranslations } from "next-intl";

import type { LeadStatus } from "@/lib/types";

const STATUS_CLASS: Record<LeadStatus, string> = {
  new: "badge-new",
  contacted: "badge-contacted",
  qualified: "badge-qualified",
  won: "badge-won",
  lost: "badge-lost",
};

interface StatusBadgeProps {
  status: LeadStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const t = useTranslations("leads.statuses");

  return (
    <span className={`badge ${STATUS_CLASS[status]}`}>
      {t(status)}
    </span>
  );
}
