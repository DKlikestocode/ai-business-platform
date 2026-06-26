import { beforeEach, describe, expect, it } from "vitest";

import { clearDashboardCache } from "@/lib/dashboard-cache";
import {
  DEFAULT_LEADS_INBOX_PREFERENCES,
  getLeadsInboxPreferences,
  normalizeLeadsInboxPreferences,
  setLeadsInboxPreferences,
} from "@/lib/leads-inbox-preferences";

describe("leads inbox preferences", () => {
  beforeEach(() => {
    clearDashboardCache();
  });

  it("returns defaults when cache is empty", () => {
    expect(getLeadsInboxPreferences()).toEqual(DEFAULT_LEADS_INBOX_PREFERENCES);
  });

  it("normalizes invalid stored values back to defaults", () => {
    expect(
      normalizeLeadsInboxPreferences({
        statusFilter: "invalid",
        qualificationFilter: "bogus",
        contactableFilter: "maybe",
        sort: "unknown_sort",
        page: 0,
      }),
    ).toEqual(DEFAULT_LEADS_INBOX_PREFERENCES);
  });

  it("persists valid filter selections across reads", () => {
    const preferences = {
      statusFilter: "contacted" as const,
      qualificationFilter: "qualified" as const,
      contactableFilter: "true" as const,
      sort: "lead_score_desc" as const,
      page: 2,
      inboxView: "archived" as const,
    };

    setLeadsInboxPreferences(preferences);
    expect(getLeadsInboxPreferences()).toEqual(preferences);
  });
});
