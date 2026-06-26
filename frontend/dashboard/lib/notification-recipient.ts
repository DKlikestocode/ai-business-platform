import type { CompanySettings } from "@/lib/types";

import { normalizeNotificationEmail } from "@/lib/notification-settings";

export function resolveNotificationRecipient(
  settings: Pick<CompanySettings, "notification_email" | "email"> | null | undefined,
): string {
  const explicit = normalizeNotificationEmail(settings?.notification_email);
  if (explicit) {
    return explicit;
  }

  return normalizeNotificationEmail(settings?.email);
}

export function isNotificationConfigured(
  settings: Pick<CompanySettings, "notification_email" | "email"> | null | undefined,
): boolean {
  return Boolean(resolveNotificationRecipient(settings));
}
