import { describe, expect, it } from "vitest";

import { getInboxStatusOptions, INBOX_LEAD_STATUSES } from "@/lib/inbox-status";

describe("inbox status options", () => {
  it("shows only owner-facing statuses for new inquiries", () => {
    expect(getInboxStatusOptions("new")).toEqual(INBOX_LEAD_STATUSES);
    expect(getInboxStatusOptions("contacted")).toEqual(INBOX_LEAD_STATUSES);
  });

  it("keeps advanced statuses visible when already set", () => {
    expect(getInboxStatusOptions("won")).toEqual(["won", "new", "contacted"]);
  });
});
