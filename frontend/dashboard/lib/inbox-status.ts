import type { LeadStatus } from "@/lib/types";

export const INBOX_LEAD_STATUSES: LeadStatus[] = ["new", "contacted"];

export function getInboxStatusOptions(current: LeadStatus): LeadStatus[] {
  if (INBOX_LEAD_STATUSES.includes(current)) {
    return INBOX_LEAD_STATUSES;
  }

  return [current, ...INBOX_LEAD_STATUSES];
}
