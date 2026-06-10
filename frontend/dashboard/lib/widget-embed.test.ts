import { describe, expect, it } from "vitest";

import { buildWidgetEmbedSnippet } from "@/lib/widget-embed";

describe("buildWidgetEmbedSnippet", () => {
  it("includes company slug and api base in the embed markup", () => {
    const snippet = buildWidgetEmbedSnippet(
      "acme-plumbing",
      "https://api.example.com",
    );

    expect(snippet).toContain('data-company-slug="acme-plumbing"');
    expect(snippet).toContain('data-api-base="https://api.example.com"');
    expect(snippet).toContain(
      '<script src="https://api.example.com/static/widget/widget.js"></script>',
    );
    expect(snippet).toContain('data-title="Chat mit uns"');
  });

  it("strips trailing slashes from the api base", () => {
    const snippet = buildWidgetEmbedSnippet(
      "acme-plumbing",
      "https://api.example.com/",
    );

    expect(snippet).toContain('data-api-base="https://api.example.com"');
    expect(snippet).not.toContain("https://api.example.com//static");
  });
});
