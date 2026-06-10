import type { LeadStatus } from "@/lib/types";
import { STATUS_LABELS } from "@/lib/types";

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
  return (
    <span className={`badge ${STATUS_CLASS[status]}`}>
      {STATUS_LABELS[status]}
    </span>
  );
}
