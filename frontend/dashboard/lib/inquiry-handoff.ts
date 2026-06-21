import type { Lead, LeadSource } from "@/lib/types";

export function hasPhone(value: string | null | undefined): value is string {
  return Boolean(value?.trim());
}

export function hasEmail(value: string | null | undefined): value is string {
  return Boolean(value?.trim());
}

export function normalizePhone(lead: Pick<Lead, "phone">): string | null {
  return hasPhone(lead.phone) ? lead.phone.trim() : null;
}

export function normalizeEmail(lead: Pick<Lead, "email">): string | null {
  return hasEmail(lead.email) ? lead.email.trim() : null;
}

export function hasContactData(lead: Pick<Lead, "phone" | "email">): boolean {
  return Boolean(normalizePhone(lead) || normalizeEmail(lead));
}

export function displayName(
  name: string | null | undefined,
  fallback: string,
): string {
  const trimmed = name?.trim();
  return trimmed ? trimmed : fallback;
}

export function handoffPreviewText(
  lead: Pick<Lead, "summary" | "description" | "service_requested">,
  fallbackLabel: string,
): string {
  const summary = lead.summary?.trim();
  if (summary) {
    return summary;
  }

  const description = lead.description?.trim();
  if (description) {
    return description;
  }

  const service = lead.service_requested?.trim();
  if (service) {
    return service;
  }

  return fallbackLabel;
}

export const INQUIRY_SOURCE_LABEL_KEY: Record<
  LeadSource,
  "sourceWebsite" | "sourceTest"
> = {
  website: "sourceWebsite",
  test: "sourceTest",
};
