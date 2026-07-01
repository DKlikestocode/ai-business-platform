const DEFAULT_PILOT_BOOKING_URL = "https://calendly.com/dominik-kessling";
const DEFAULT_PILOT_BOOKING_MAILTO =
  "mailto:Dominik.Kessling@gmail.com?subject=AI%20Anfragen-Assistent%20Demo%20anfragen";

export function getPilotBookingUrl(): string {
  const configured = process.env.NEXT_PUBLIC_PILOT_BOOKING_URL?.trim();
  if (configured === "mailto") {
    return DEFAULT_PILOT_BOOKING_MAILTO;
  }
  if (configured) {
    return configured;
  }
  return DEFAULT_PILOT_BOOKING_URL;
}

export function isExternalPilotBookingUrl(url: string): boolean {
  return url.startsWith("http://") || url.startsWith("https://");
}
