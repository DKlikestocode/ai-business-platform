const DEFAULT_PILOT_BOOKING_MAILTO =
  "mailto:hallo@dominiksdomain.com?subject=AuftragsPilot%20Pilot%20anfragen";

export function getPilotBookingUrl(): string {
  const configured = process.env.NEXT_PUBLIC_PILOT_BOOKING_URL?.trim();
  if (configured) {
    return configured;
  }
  return DEFAULT_PILOT_BOOKING_MAILTO;
}

export function isExternalPilotBookingUrl(url: string): boolean {
  return url.startsWith("http://") || url.startsWith("https://");
}
