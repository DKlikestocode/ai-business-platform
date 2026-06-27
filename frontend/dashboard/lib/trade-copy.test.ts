import { describe, expect, it, vi } from "vitest";

import { translateWithTradeOverride } from "@/lib/trade-copy";

describe("translateWithTradeOverride", () => {
  it("returns trade copy when override exists", () => {
    const result = translateWithTradeOverride(
      () => "Generic text",
      () => "SKH text",
      "welcomeLead",
      true,
    );

    expect(result).toBe("SKH text");
  });

  it("falls back to default when trade key is missing", () => {
    const result = translateWithTradeOverride(
      () => "Generic text",
      (key) => `trades.skh.gettingStarted.${key}`,
      "welcomeLead",
      true,
    );

    expect(result).toBe("Generic text");
  });

  it("uses default when trade is disabled", () => {
    const tDefault = vi.fn(() => "Generic text");
    const tTrade = vi.fn(() => "SKH text");

    const result = translateWithTradeOverride(
      tDefault,
      tTrade,
      "welcomeLead",
      false,
    );

    expect(result).toBe("Generic text");
    expect(tTrade).not.toHaveBeenCalled();
  });
});
