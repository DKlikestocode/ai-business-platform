import { formatDateTime } from "@/lib/format-datetime";

export function isInquiryContacted(
  contactedAt: string | null | undefined,
): boolean {
  return Boolean(contactedAt?.trim());
}

export function formatInquiryContactedTimestamp(
  contactedAt: string | null | undefined,
  locale: string,
  dateStyle: "full" | "medium" = "medium",
): string | null {
  if (!isInquiryContacted(contactedAt)) {
    return null;
  }

  return formatDateTime(contactedAt, locale, dateStyle);
}
