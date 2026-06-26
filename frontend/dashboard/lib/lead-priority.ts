export interface PriorityScoreFactor {
  key: string;
  points: number;
}

export const PRIORITY_SCORE_FACTORS: PriorityScoreFactor[] = [
  { key: "contact", points: 25 },
  { key: "description", points: 20 },
  { key: "location", points: 10 },
  { key: "postalCode", points: 5 },
  { key: "service", points: 15 },
  { key: "urgency", points: 10 },
  { key: "name", points: 10 },
  { key: "callback", points: 5 },
];

export const MAX_PRIORITY_SCORE = PRIORITY_SCORE_FACTORS.reduce(
  (total, factor) => total + factor.points,
  0,
);

export function formatPriorityThreshold(value: number): string {
  return String(Math.max(0, Math.min(100, value)));
}

export function meetsContactablePriorityThreshold(
  score: number,
  threshold: number,
): boolean {
  return score >= threshold;
}
