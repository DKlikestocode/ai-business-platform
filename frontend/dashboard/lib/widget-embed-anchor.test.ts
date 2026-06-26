import { describe, expect, it } from "vitest";

import {
  SETTINGS_WIDGET_EMBED_HREF,
  WIDGET_EMBED_SECTION_ID,
} from "@/lib/widget-embed-anchor";

describe("widget embed anchor", () => {
  it("exposes a stable settings hash link", () => {
    expect(WIDGET_EMBED_SECTION_ID).toBe("widget-embed");
    expect(SETTINGS_WIDGET_EMBED_HREF).toBe("/settings#widget-embed");
  });
});
