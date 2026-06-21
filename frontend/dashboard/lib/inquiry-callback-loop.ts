import type { LeadStatus } from "@/lib/types";

export type PrimaryContactAction = "phone" | "email" | "none";

export function shouldPromptMarkContacted(status: LeadStatus): boolean {
  return status === "new";
}

export function getPrimaryContactAction(
  phone: string | null,
  email: string | null,
): PrimaryContactAction {
  if (phone) {
    return "phone";
  }
  if (email) {
    return "email";
  }
  return "none";
}

export function shouldShowMarkContactedAction(
  hasContact: boolean,
  status: LeadStatus,
): boolean {
  return hasContact && shouldPromptMarkContacted(status);
}
