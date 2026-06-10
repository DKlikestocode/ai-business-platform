import type { ContactMethod, QualificationStatus } from "@/lib/types";

export const QUALIFICATION_STATUSES: QualificationStatus[] = [
  "incomplete",
  "contactable",
  "qualified",
];

export const QUALIFICATION_BADGE_CLASS: Record<QualificationStatus, string> = {
  incomplete: "badge-qual-incomplete",
  contactable: "badge-qual-contactable",
  qualified: "badge-qual-qualified",
};

export type LeadSort = "created_at_desc" | "lead_score_desc";

export const LEAD_SORT_OPTIONS: LeadSort[] = [
  "created_at_desc",
  "lead_score_desc",
];

export function formatLeadScore(value: number): string {
  return String(value);
}

export function contactableBadgeClass(value: boolean): string {
  return value ? "badge-contactable-yes" : "badge-contactable-no";
}

export function isKnownContactMethod(
  value: ContactMethod | null | undefined,
): value is ContactMethod {
  return value === "phone" ||
    value === "email" ||
    value === "channel" ||
    value === "unknown";
}
