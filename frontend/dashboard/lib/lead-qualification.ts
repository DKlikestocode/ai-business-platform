import type { ContactMethod, QualificationStatus } from "@/lib/types";

export const QUALIFICATION_STATUSES: QualificationStatus[] = [
  "incomplete",
  "contactable",
  "qualified",
];

export const QUALIFICATION_LABELS: Record<QualificationStatus, string> = {
  incomplete: "Incomplete",
  contactable: "Contactable",
  qualified: "Qualified",
};

export const QUALIFICATION_BADGE_CLASS: Record<QualificationStatus, string> = {
  incomplete: "badge-qual-incomplete",
  contactable: "badge-qual-contactable",
  qualified: "badge-qual-qualified",
};

export const CONTACT_METHOD_LABELS: Record<ContactMethod, string> = {
  phone: "Phone",
  email: "Email",
  channel: "Channel",
  unknown: "Unknown",
};

export type LeadSort = "created_at_desc" | "lead_score_desc";

export const LEAD_SORT_OPTIONS: { value: LeadSort; label: string }[] = [
  { value: "created_at_desc", label: "Newest first" },
  { value: "lead_score_desc", label: "Highest score" },
];

export function formatContactable(value: boolean): string {
  return value ? "Yes" : "No";
}

export function formatContactMethod(
  value: ContactMethod | null | undefined,
): string {
  if (!value) {
    return "—";
  }
  return CONTACT_METHOD_LABELS[value];
}

export function formatLeadScore(value: number): string {
  return String(value);
}

export function contactableBadgeClass(value: boolean): string {
  return value ? "badge-contactable-yes" : "badge-contactable-no";
}
