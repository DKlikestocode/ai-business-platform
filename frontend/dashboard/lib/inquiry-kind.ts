export type InquiryKind = "appointment_consultation" | "quote" | "unknown";

export type InquiryKindFilter = "appointment_consultation" | "quote";

export const INQUIRY_KIND_FILTER_OPTIONS: InquiryKindFilter[] = [
  "appointment_consultation",
  "quote",
];

export const INQUIRY_KIND_CATEGORY_TAB_KEY: Record<InquiryKindFilter, string> = {
  appointment_consultation: "categoryTabAppointment",
  quote: "categoryTabQuote",
};

export const INQUIRY_KIND_LABEL_KEY: Record<InquiryKind, string> = {
  appointment_consultation: "inquiryKindAppointment",
  quote: "inquiryKindQuote",
  unknown: "inquiryKindUnknown",
};

export const INQUIRY_KIND_BADGE_CLASS: Record<InquiryKind, string> = {
  appointment_consultation: "badge-inquiry-appointment",
  quote: "badge-inquiry-quote",
  unknown: "badge-inquiry-unknown",
};

export function isInquiryKindFilter(value: unknown): value is InquiryKindFilter {
  return value === "appointment_consultation" || value === "quote";
}

export function normalizeInquiryKind(value: unknown): InquiryKind {
  if (value === "appointment_consultation" || value === "quote") {
    return value;
  }
  return "unknown";
}
