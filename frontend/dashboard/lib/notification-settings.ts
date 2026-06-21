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

export function areNotificationRecipientSettingsDirty(
  saved: Pick<CompanySettings, "notification_email" | "email">,
  draft: Pick<CompanySettings, "notification_email" | "email">,
): boolean {
  return (
    normalizeNotificationEmail(saved.notification_email) !==
      normalizeNotificationEmail(draft.notification_email) ||
    normalizeNotificationEmail(saved.email) !==
      normalizeNotificationEmail(draft.email)
  );
}

export function canSendTestNotification(
  savedSettings: Pick<CompanySettings, "notification_email" | "email"> | null,
  draftSettings: Pick<CompanySettings, "notification_email" | "email"> | null,
): boolean {
  if (!savedSettings || !draftSettings) {
    return false;
  }

  const savedRecipient = resolveNotificationRecipient(savedSettings);
  return (
    Boolean(savedRecipient) &&
    !areNotificationRecipientSettingsDirty(savedSettings, draftSettings)
  );
}
