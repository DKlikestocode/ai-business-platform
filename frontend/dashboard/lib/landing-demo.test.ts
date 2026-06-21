import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import {
  createLandingDemoConversationId,
  isLandingDemoLimitStatus,
  isValidLandingDemoConversationId,
} from "@/lib/landing-demo";

describe("landing demo conversation ids", () => {
  it("creates ids with the landing demo prefix", () => {
    const conversationId = createLandingDemoConversationId();
    expect(isValidLandingDemoConversationId(conversationId)).toBe(true);
    expect(conversationId).toMatch(/^landing-demo-\d+$/);
  });
});

describe("landing demo limits", () => {
  it("detects rate limit responses", () => {
    expect(isLandingDemoLimitStatus(429)).toBe(true);
    expect(isLandingDemoLimitStatus(200)).toBe(false);
  });
});

describe("landing demo German copy", () => {
  it("describes a live demo instead of scripted scenarios", () => {
    expect(de.landing.publicDemo.disclaimer).toContain("Demo");
    expect(de.landing.publicDemo.thinking).toBeTruthy();
    expect(de.landing.publicDemo.limitReached).toBeTruthy();
    expect(de.landing.publicDemo.starters.plumber).toBeTruthy();
  });

  it("does not expose old scripted assistant messages", () => {
    const publicDemo = de.landing.publicDemo as Record<string, unknown>;
    expect(publicDemo.scenarios).toBeUndefined();
  });
});
