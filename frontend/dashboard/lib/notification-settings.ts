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
  savedEmail: string | null | undefined,
  draftEmail: string | null | undefined,
): boolean {
  const saved = normalizeNotificationEmail(savedEmail);
  return Boolean(saved) && !isNotificationEmailDirty(savedEmail, draftEmail);
}
