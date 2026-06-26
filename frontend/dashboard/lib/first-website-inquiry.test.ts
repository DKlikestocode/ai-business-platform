import { describe, expect, it } from "vitest";

import { shouldShowFirstWebsiteInquiryMarker } from "@/lib/first-website-inquiry";
import type { Lead } from "@/lib/types";

function buildLead(overrides: Partial<Lead> = {}): Lead {
  return {
    id: "lead-1",
    company_id: "company-1",
    conversation_id: "conv-1",
    source: "website",
    is_first_website_inquiry: false,
    name: "Max Mustermann",
    phone: "555-0100",
    email: null,
    company: null,
    location: "Berlin",
    postal_code: "10115",
    service_area_status: null,
    service_area_distance_km: null,
    service_requested: "Dach",
    description: "Undichtes Dach",
    urgency: "hoch",
    preferred_callback_time: "Morgen",
    status: "new",
    summary: null,
    contactable: true,
    contact_method: "phone",
    lead_score: 80,
    qualification_status: "qualified",
    notification_sent_at: null,
    contacted_at: null,
    archived_at: null,
    created_at: "2026-06-21T10:00:00Z",
    ...overrides,
  };
}

describe("shouldShowFirstWebsiteInquiryMarker", () => {
  it("renders marker for first real website inquiry", () => {
    expect(
      shouldShowFirstWebsiteInquiryMarker(
        buildLead({ is_first_website_inquiry: true }),
      ),
    ).toBe(true);
  });

  it("does not render marker for test inquiries", () => {
    expect(
      shouldShowFirstWebsiteInquiryMarker(
        buildLead({
          source: "test",
          is_first_website_inquiry: true,
        }),
      ),
    ).toBe(false);
  });

  it("does not render marker for later website inquiries", () => {
    expect(
      shouldShowFirstWebsiteInquiryMarker(
        buildLead({ is_first_website_inquiry: false }),
      ),
    ).toBe(false);
  });
});
