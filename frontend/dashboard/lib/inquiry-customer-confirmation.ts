import { formatDateTime } from "@/lib/format-datetime";

export type CustomerConfirmationStatus = "sent" | "not_sent";

export function isCustomerConfirmationSent(
  customerConfirmationSentAt: string | null | undefined,
): boolean {
  return Boolean(customerConfirmationSentAt?.trim());
}

export function getCustomerConfirmationStatus(
  customerConfirmationSentAt: string | null | undefined,
): CustomerConfirmationStatus {
  return isCustomerConfirmationSent(customerConfirmationSentAt)
    ? "sent"
    : "not_sent";
}

export function formatCustomerConfirmationTimestamp(
  customerConfirmationSentAt: string | null | undefined,
  locale: string,
  dateStyle: "full" | "medium" = "medium",
): string | null {
  if (!isCustomerConfirmationSent(customerConfirmationSentAt)) {
    return null;
  }

  return formatDateTime(customerConfirmationSentAt, locale, dateStyle);
}

export function shouldShowCustomerConfirmationIndicator(
  sendCustomerConfirmation: boolean,
  customerConfirmationSentAt: string | null | undefined,
): boolean {
  return sendCustomerConfirmation || isCustomerConfirmationSent(customerConfirmationSentAt);
}
