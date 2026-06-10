"use client";

import { useTranslations } from "next-intl";

import type { LeadStatus } from "@/lib/types";
import { LEAD_STATUSES } from "@/lib/types";

interface StatusSelectProps {
  value: LeadStatus;
  onChange: (status: LeadStatus) => void;
  disabled?: boolean;
}

export function StatusSelect({ value, onChange, disabled }: StatusSelectProps) {
  const t = useTranslations("leads");
  const tStatuses = useTranslations("leads.statuses");

  return (
    <select
      className="select"
      value={value}
      disabled={disabled}
      onChange={(event) => onChange(event.target.value as LeadStatus)}
      aria-label={t("updateStatusAria")}
    >
      {LEAD_STATUSES.map((status) => (
        <option key={status} value={status}>
          {tStatuses(status)}
        </option>
      ))}
    </select>
  );
}
