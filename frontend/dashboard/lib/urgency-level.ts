export type UrgencyLevel = "high" | "medium" | "low";

const URGENCY_HIGH = new Set(["high", "hoch", "dringend", "urgent"]);
const URGENCY_MEDIUM = new Set(["medium", "mittel"]);
const URGENCY_LOW = new Set(["low", "niedrig"]);

export function parseUrgencyLevel(
  value: string | null | undefined,
): UrgencyLevel | null {
  const normalized = value?.trim().toLowerCase() ?? "";
  if (!normalized) {
    return null;
  }
  if (URGENCY_HIGH.has(normalized)) {
    return "high";
  }
  if (URGENCY_MEDIUM.has(normalized)) {
    return "medium";
  }
  if (URGENCY_LOW.has(normalized)) {
    return "low";
  }
  return null;
}

export function formatUrgencyLabel(
  value: string | null | undefined,
  translateLevel: (level: UrgencyLevel) => string,
): string | null {
  const level = parseUrgencyLevel(value);
  if (level) {
    return translateLevel(level);
  }
  const trimmed = value?.trim();
  return trimmed || null;
}
