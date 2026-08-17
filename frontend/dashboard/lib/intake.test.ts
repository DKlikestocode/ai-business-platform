import { describe, expect, it } from "vitest";

import {
  canExportIntake,
  canReviewIntake,
  formatFileSize,
  intakeDisplayName,
} from "@/lib/intake";
import type { IntakeItem } from "@/lib/types";

const item = {
  customer_name: null,
  customer_company: "Muster GmbH",
  sender_name: "Maria Muster",
  sender_email: "maria@example.com",
} as IntakeItem;

describe("intake helpers", () => {
  it("uses the best available customer label", () => {
    expect(intakeDisplayName(item)).toBe("Muster GmbH");
  });

  it("allows review and export only in safe states", () => {
    expect(canReviewIntake("needs_review")).toBe(true);
    expect(canReviewIntake("processing")).toBe(false);
    expect(canExportIntake("ready")).toBe(true);
    expect(canExportIntake("needs_review")).toBe(false);
  });

  it("formats attachment sizes", () => {
    expect(formatFileSize(1536, "de-DE")).toBe("1,5 KB");
  });
});
