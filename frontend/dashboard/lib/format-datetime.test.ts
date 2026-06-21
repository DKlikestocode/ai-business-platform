import { describe, expect, it } from "vitest";

import { formatDateTime } from "@/lib/format-datetime";

describe("formatDateTime", () => {
  it("formats valid ISO timestamps", () => {
    const formatted = formatDateTime("2026-06-10T12:00:00Z", "de", "medium");

    expect(formatted).toBeTruthy();
    expect(formatted).toContain("2026");
  });

  it("returns null for invalid timestamps", () => {
    expect(formatDateTime("not-a-date", "de")).toBeNull();
  });

  it("returns null for empty values", () => {
    expect(formatDateTime(null, "de")).toBeNull();
    expect(formatDateTime("", "de")).toBeNull();
  });
});
