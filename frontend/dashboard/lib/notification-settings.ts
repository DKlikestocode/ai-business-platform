import type { CompanySettings } from "@/lib/types";
import { resolveNotificationRecipient } from "@/lib/notification-recipient";

export function normalizeNotificationEmail(
  email: string | null | undefined,
): string {
  return email?.trim() ?? "";
}

export function isNotificationEmailDirty(
  savedEmail: string | null | undefined,
  draftEmail: string | null | undefined,
): boolean {
  return (
    normalizeNotificationEmail(savedEmail) !==
    normalizeNotificationEmail(draftEmail)
  );
}

export function canSendTestNotification(
  savedSettings: CompanySettings | null | undefined,
  draftSettings: CompanySettings | null | undefined,
): boolean {
  if (!savedSettings || !draftSettings) {
    return false;
  }

  if (
    isNotificationEmailDirty(
      savedSettings.notification_email,
      draftSettings.notification_email,
    )
  ) {
    return false;
  }

  if (
    normalizeNotificationEmail(savedSettings.email) !==
    normalizeNotificationEmail(draftSettings.email)
  ) {
    return false;
  }

  return Boolean(resolveNotificationRecipient(savedSettings));
}
