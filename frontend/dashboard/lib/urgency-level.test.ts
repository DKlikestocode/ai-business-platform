import { describe, expect, it } from "vitest";

import {
  formatUrgencyLabel,
  parseUrgencyLevel,
} from "@/lib/urgency-level";

describe("urgency level", () => {
  it("parses German and English urgency tiers", () => {
    expect(parseUrgencyLevel("hoch")).toBe("high");
    expect(parseUrgencyLevel("HIGH")).toBe("high");
    expect(parseUrgencyLevel("mittel")).toBe("medium");
    expect(parseUrgencyLevel("medium")).toBe("medium");
    expect(parseUrgencyLevel("niedrig")).toBe("low");
    expect(parseUrgencyLevel("low")).toBe("low");
    expect(parseUrgencyLevel("")).toBeNull();
    expect(parseUrgencyLevel("unbekannt")).toBeNull();
  });

  it("formats known tiers via translator", () => {
    const labels: Record<string, string> = {
      high: "Hoch",
      medium: "Mittel",
      low: "Niedrig",
    };
    expect(formatUrgencyLabel("hoch", (level) => labels[level])).toBe("Hoch");
    expect(formatUrgencyLabel("custom text", (level) => labels[level])).toBe(
      "custom text",
    );
  });
});
