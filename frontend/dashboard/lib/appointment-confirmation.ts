import { formatDateTime } from "@/lib/format-datetime";
import type { InquiryKind, Lead } from "@/lib/types";

export type AppointmentConfirmationPreference = "email" | "sms" | "none";

export function isAppointmentInquiry(lead: Pick<Lead, "inquiry_kind" | "preferred_callback_time">): boolean {
  if (lead.inquiry_kind === "appointment_consultation") {
    return true;
  }
  return Boolean(lead.preferred_callback_time?.trim());
}

export function formatAppointmentConfirmationPreference(
  preference: string | null | undefined,
  translate: (key: AppointmentConfirmationPreference | "pending") => string,
): string {
  if (preference === "email" || preference === "sms" || preference === "none") {
    return translate(preference);
  }
  return translate("pending");
}

export function isAppointmentConfirmationSent(
  appointmentConfirmationSentAt: string | null | undefined,
): boolean {
  return Boolean(appointmentConfirmationSentAt?.trim());
}

export function formatAppointmentConfirmationSentAt(
  appointmentConfirmationSentAt: string | null | undefined,
  locale: string,
): string | null {
  if (!isAppointmentConfirmationSent(appointmentConfirmationSentAt)) {
    return null;
  }
  return formatDateTime(appointmentConfirmationSentAt, locale, "full");
}

export function buildLeadCalendarIcsPath(leadId: string): string {
  return `/api/v1/leads/${leadId}/calendar.ics`;
}

export function canSendAppointmentConfirmationEmail(
  lead: Pick<Lead, "email" | "appointment_confirmation_sent_at">,
): boolean {
  const email = lead.email?.trim();
  if (!email) {
    return false;
  }
  return !isAppointmentConfirmationSent(lead.appointment_confirmation_sent_at);
}
