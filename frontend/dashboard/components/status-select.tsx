"use client";

import type { LeadStatus } from "@/lib/types";
import { LEAD_STATUSES, STATUS_LABELS } from "@/lib/types";

interface StatusSelectProps {
  value: LeadStatus;
  onChange: (status: LeadStatus) => void;
  disabled?: boolean;
}

export function StatusSelect({ value, onChange, disabled }: StatusSelectProps) {
  return (
    <select
      className="select"
      value={value}
      disabled={disabled}
      onChange={(event) => onChange(event.target.value as LeadStatus)}
      aria-label="Update lead status"
    >
      {LEAD_STATUSES.map((status) => (
        <option key={status} value={status}>
          {STATUS_LABELS[status]}
        </option>
      ))}
    </select>
  );
}
