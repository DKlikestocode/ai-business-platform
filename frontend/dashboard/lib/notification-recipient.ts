import type { CompanySettings } from "@/lib/types";

import { normalizeNotificationEmail } from "@/lib/notification-settings";

export function resolveNotificationRecipient(
  settings: Pick<CompanySettings, "notification_email" | "email"> | null | undefined,
): string {
  if (!settings) {
    return "";
  }

  return (
    normalizeNotificationEmail(settings.notification_email) ||
    normalizeNotificationEmail(settings.email)
  );
}

export function isNotificationRecipientConfigured(
  settings: Pick<CompanySettings, "notification_email" | "email"> | null | undefined,
): boolean {
  return Boolean(resolveNotificationRecipient(settings));
}
