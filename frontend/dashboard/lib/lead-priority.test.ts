import { describe, expect, it } from "vitest";

import {
  MAX_PRIORITY_SCORE,
  PRIORITY_SCORE_FACTORS,
  formatPriorityThreshold,
  meetsContactablePriorityThreshold,
} from "@/lib/lead-priority";

describe("lead priority helpers", () => {
  it("matches backend scoring weights", () => {
    expect(MAX_PRIORITY_SCORE).toBe(100);
    expect(PRIORITY_SCORE_FACTORS).toHaveLength(7);
    expect(PRIORITY_SCORE_FACTORS[0]).toEqual({ key: "contact", points: 25 });
  });

  it("clamps threshold display values", () => {
    expect(formatPriorityThreshold(60)).toBe("60");
    expect(formatPriorityThreshold(150)).toBe("100");
    expect(formatPriorityThreshold(-5)).toBe("0");
  });

  it("checks contactable notification threshold", () => {
    expect(meetsContactablePriorityThreshold(60, 50)).toBe(true);
    expect(meetsContactablePriorityThreshold(40, 50)).toBe(false);
  });
});
