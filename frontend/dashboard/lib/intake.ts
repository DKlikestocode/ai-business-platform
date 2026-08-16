import type { IntakeItem, IntakeStatus } from "@/lib/types";

export const INTAKE_FILTER_STATUSES: IntakeStatus[] = [
  "needs_review",
  "ready",
  "processing",
  "received",
  "failed",
  "exported",
  "discarded",
];

export function intakeDisplayName(item: IntakeItem): string {
  return (
    item.customer_name?.trim() ||
    item.customer_company?.trim() ||
    item.sender_name?.trim() ||
    item.sender_email?.trim() ||
    "—"
  );
}

export function canReviewIntake(status: IntakeStatus): boolean {
  return ["ready", "needs_review", "failed", "exported"].includes(status);
}

export function canExportIntake(status: IntakeStatus): boolean {
  return status === "ready" || status === "exported";
}

export function formatFileSize(sizeBytes: number, locale: string): string {
  if (sizeBytes < 1024) {
    return `${sizeBytes} B`;
  }
  if (sizeBytes < 1024 * 1024) {
    return `${new Intl.NumberFormat(locale, { maximumFractionDigits: 1 }).format(sizeBytes / 1024)} KB`;
  }
  return `${new Intl.NumberFormat(locale, { maximumFractionDigits: 1 }).format(sizeBytes / (1024 * 1024))} MB`;
}
