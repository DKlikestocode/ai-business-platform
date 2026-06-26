"use client";

import { useTranslations } from "next-intl";

import type { LeadStatus } from "@/lib/types";

const STATUS_CLASS: Record<"new" | "contacted", string> = {
  new: "badge-new",
  contacted: "badge-contacted",
};

function displayStatus(status: LeadStatus): "new" | "contacted" {
  return status === "new" ? "new" : "contacted";
}

interface StatusBadgeProps {
  status: LeadStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const t = useTranslations("leads.statuses");
  const resolved = displayStatus(status);

  return (
    <span className={`badge ${STATUS_CLASS[resolved]}`}>
      {t(resolved)}
    </span>
  );
}
