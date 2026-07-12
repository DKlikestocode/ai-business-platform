import { describe, expect, it } from "vitest";

import {
  buildLeadCalendarIcsPath,
  canSendAppointmentConfirmationEmail,
  formatAppointmentConfirmationPreference,
  isAppointmentInquiry,
} from "@/lib/appointment-confirmation";
import type { Lead } from "@/lib/types";

function makeLead(overrides: Partial<Lead> = {}): Lead {
  return {
    id: "lead-1",
    company_id: "company-1",
    conversation_id: "conv-1",
    source: "website",
    is_first_website_inquiry: false,
    name: "Max Mustermann",
    phone: "+49 170 1234567",
    email: "max@example.com",
    company: null,
    location: "Berlin",
    postal_code: "10115",
    service_area_status: null,
    service_area_distance_km: null,
    service_requested: "Sanitär-Notfall",
    description: "Küchenspüle läuft aus",
    urgency: "Dringend",
    preferred_callback_time: "Vormittags",
    status: "new",
    summary: null,
    contactable: true,
    contact_method: "phone",
    lead_score: 80,
    qualification_status: "contactable",
    inquiry_kind: "appointment_consultation",
    notification_sent_at: null,
    customer_confirmation_sent_at: null,
    appointment_confirmation_preference: null,
    appointment_confirmation_sent_at: null,
    contacted_at: null,
    archived_at: null,
    created_at: "2025-06-01T10:00:00Z",
    ...overrides,
  };
}

describe("appointment confirmation helpers", () => {
  it("detects appointment inquiries", () => {
    expect(isAppointmentInquiry(makeLead())).toBe(true);
    expect(
      isAppointmentInquiry(
        makeLead({ inquiry_kind: "quote", preferred_callback_time: "" }),
      ),
    ).toBe(false);
    expect(
      isAppointmentInquiry(
        makeLead({ inquiry_kind: "quote", preferred_callback_time: "Montag" }),
      ),
    ).toBe(true);
  });

  it("formats confirmation preference labels", () => {
    const translate = (key: string) => `label:${key}`;
    expect(formatAppointmentConfirmationPreference("email", translate)).toBe("label:email");
    expect(formatAppointmentConfirmationPreference(null, translate)).toBe("label:pending");
  });

  it("builds calendar ICS API path", () => {
    expect(buildLeadCalendarIcsPath("abc-123")).toBe("/api/v1/leads/abc-123/calendar.ics");
  });

  it("allows email confirmation only when email exists and not sent", () => {
    expect(canSendAppointmentConfirmationEmail(makeLead())).toBe(true);
    expect(canSendAppointmentConfirmationEmail(makeLead({ email: null }))).toBe(false);
    expect(
      canSendAppointmentConfirmationEmail(
        makeLead({ appointment_confirmation_sent_at: "2025-06-02T10:00:00Z" }),
      ),
    ).toBe(false);
  });
});
