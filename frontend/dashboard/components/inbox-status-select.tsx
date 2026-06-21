"use client";

import { useTranslations } from "next-intl";

import { getInboxStatusOptions } from "@/lib/inbox-status";
import type { LeadStatus } from "@/lib/types";

interface InboxStatusSelectProps {
  value: LeadStatus;
  onChange: (status: LeadStatus) => void;
  disabled?: boolean;
}

export function InboxStatusSelect({ value, onChange, disabled }: InboxStatusSelectProps) {
  const t = useTranslations("leads");
  const tStatuses = useTranslations("leads.statuses");
  const options = getInboxStatusOptions(value);

  return (
    <select
      className="select"
      value={value}
      disabled={disabled}
      onChange={(event) => onChange(event.target.value as LeadStatus)}
      aria-label={t("updateStatusAria")}
    >
      {options.map((status) => (
        <option key={status} value={status}>
          {tStatuses(status)}
        </option>
      ))}
    </select>
  );
}
