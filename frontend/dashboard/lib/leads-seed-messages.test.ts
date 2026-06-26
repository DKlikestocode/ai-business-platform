import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import en from "@/messages/en.json";

describe("leads seed demo copy", () => {
  it("defines localized already-exists feedback in DE and EN", () => {
    expect(de.leads.seedAlreadyExist).toContain("Posteingang");
    expect(en.leads.seedAlreadyExist).toContain("inbox");
  });
});
