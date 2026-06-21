import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import en from "@/messages/en.json";
import {
  INQUIRY_SOURCE_LABEL_KEY,
  displayName,
  handoffPreviewText,
  hasContactData,
  normalizeEmail,
  normalizePhone,
} from "@/lib/inquiry-handoff";
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
    notification_sent_at: null,
    created_at: "2025-06-01T10:00:00Z",
    ...overrides,
  };
}

describe("inquiry handoff helpers", () => {
  it("normalizes full contact data", () => {
    const lead = makeLead();
    expect(normalizePhone(lead)).toBe("+49 170 1234567");
    expect(normalizeEmail(lead)).toBe("max@example.com");
    expect(hasContactData(lead)).toBe(true);
  });

  it("handles missing phone", () => {
    const lead = makeLead({ phone: "  " });
    expect(normalizePhone(lead)).toBeNull();
    expect(hasContactData(lead)).toBe(true);
  });

  it("handles missing email", () => {
    const lead = makeLead({ email: null });
    expect(normalizeEmail(lead)).toBeNull();
    expect(hasContactData(lead)).toBe(true);
  });

  it("detects when all contact data is missing", () => {
    const lead = makeLead({ phone: "", email: null });
    expect(hasContactData(lead)).toBe(false);
  });

  it("prefers summary over description and service", () => {
    const lead = makeLead({
      summary: "Kurze Zusammenfassung",
      description: "Lange Beschreibung",
      service_requested: "Sanitär",
    });
    expect(handoffPreviewText(lead, "Keine Beschreibung")).toBe(
      "Kurze Zusammenfassung",
    );
  });

  it("falls back to description when summary is empty", () => {
    const lead = makeLead({
      summary: null,
      description: "Lange Beschreibung",
      service_requested: "Sanitär",
    });
    expect(handoffPreviewText(lead, "Keine Beschreibung")).toBe(
      "Lange Beschreibung",
    );
  });

  it("falls back to service when summary and description are empty", () => {
    const lead = makeLead({
      summary: null,
      description: "",
      service_requested: "Sanitär",
    });
    expect(handoffPreviewText(lead, "Keine Beschreibung")).toBe("Sanitär");
  });

  it("uses fallback label when no handoff text exists", () => {
    const lead = makeLead({
      summary: null,
      description: "",
      service_requested: "  ",
    });
    expect(handoffPreviewText(lead, "Keine Beschreibung")).toBe(
      "Keine Beschreibung",
    );
  });

  it("returns trimmed name when present", () => {
    expect(displayName(" Max Mustermann ", "Unbekannt")).toBe("Max Mustermann");
  });

  it("returns fallback for empty or whitespace name", () => {
    expect(displayName("", "Unbekannt")).toBe("Unbekannt");
    expect(displayName("   ", "Unbekannt")).toBe("Unbekannt");
    expect(displayName(null, "Unbekannt")).toBe("Unbekannt");
    expect(displayName(undefined, "Unbekannt")).toBe("Unbekannt");
  });

  it("maps inquiry sources to i18n label keys", () => {
    expect(INQUIRY_SOURCE_LABEL_KEY.website).toBe("sourceWebsite");
    expect(INQUIRY_SOURCE_LABEL_KEY.test).toBe("sourceTest");
    expect(de.leads.sourceWebsite).toBe("Website");
    expect(de.leads.sourceTest).toBe("Test");
    expect(en.leads.sourceWebsite).toBe("Website");
    expect(en.leads.sourceTest).toBe("Test");
  });

  it("uses the same unknown contact label in inbox and detail", () => {
    expect(de.leads.unknownContact).toBe(de.leadDetail.unknownContact);
    expect(en.leads.unknownContact).toBe(en.leadDetail.unknownContact);
  });
});
