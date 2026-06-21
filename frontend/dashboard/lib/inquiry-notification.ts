import { formatDateTime } from "@/lib/format-datetime";

export type InquiryNotificationStatus = "sent" | "not_sent";

export function isInquiryNotificationSent(
  notificationSentAt: string | null | undefined,
): boolean {
  return Boolean(notificationSentAt?.trim());
}

export function getInquiryNotificationStatus(
  notificationSentAt: string | null | undefined,
): InquiryNotificationStatus {
  return isInquiryNotificationSent(notificationSentAt) ? "sent" : "not_sent";
}

export function formatInquiryNotificationTimestamp(
  notificationSentAt: string | null | undefined,
  locale: string,
  dateStyle: "full" | "medium" = "medium",
): string | null {
  if (!isInquiryNotificationSent(notificationSentAt)) {
    return null;
  }

  return formatDateTime(notificationSentAt, locale, dateStyle);
}
