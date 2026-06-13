import { describe, expect, it } from "vitest";

import {
  activationStatusClassName,
  embedSnippetIncludesInstallToken,
  formatActivationTimestamp,
  isActivationSetupLive,
} from "@/lib/activation-display";

describe("activation display helpers", () => {
  it("formats activation timestamps for the locale", () => {
    const formatted = formatActivationTimestamp("2025-06-01T10:00:00.000Z", "de-DE");

    expect(formatted).toBeTruthy();
    expect(formatted).toContain("2025");
  });

  it("returns null for missing or invalid timestamps", () => {
    expect(formatActivationTimestamp(null, "de-DE")).toBeNull();
    expect(formatActivationTimestamp("invalid", "de-DE")).toBeNull();
  });

  it("maps activation status to css classes", () => {
    expect(activationStatusClassName("live")).toBe(
      "activation-status activation-status--live",
    );
  });

  it("detects install key in server embed snippets", () => {
    expect(
      embedSnippetIncludesInstallToken(
        '<div data-install-token="abc"></div>',
      ),
    ).toBe(true);
    expect(embedSnippetIncludesInstallToken("<div></div>")).toBe(false);
  });

  it("treats only live activation as website setup complete", () => {
    expect(isActivationSetupLive("live")).toBe(true);
    expect(isActivationSetupLive("awaiting_widget")).toBe(false);
    expect(isActivationSetupLive("setup_incomplete")).toBe(false);
    expect(isActivationSetupLive("stale")).toBe(false);
    expect(isActivationSetupLive(null)).toBe(false);
  });

  it("identifies server embed snippets suitable for customer copy", () => {
    const snippet = [
      '<div id="ai-agent-widget"',
      'data-company-slug="acme"',
      'data-install-token="secret-key"',
      'data-api-base="https://example.com"></div>',
      '<script src="https://example.com/static/widget/widget.js"></script>',
    ].join(" ");

    expect(embedSnippetIncludesInstallToken(snippet)).toBe(true);
    expect(snippet).toContain("data-install-token=");
  });
});
