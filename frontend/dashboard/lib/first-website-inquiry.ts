import type { Lead } from "@/lib/types";

export function shouldShowFirstWebsiteInquiryMarker(lead: Lead): boolean {
  return lead.source === "website" && lead.is_first_website_inquiry;
}
