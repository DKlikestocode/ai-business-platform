import {
  QUALIFICATION_BADGE_CLASS,
  QUALIFICATION_LABELS,
} from "@/lib/lead-qualification";
import type { QualificationStatus } from "@/lib/types";

interface QualificationBadgeProps {
  status: QualificationStatus;
}

export function QualificationBadge({ status }: QualificationBadgeProps) {
  return (
    <span className={`badge ${QUALIFICATION_BADGE_CLASS[status]}`}>
      {QUALIFICATION_LABELS[status]}
    </span>
  );
}
