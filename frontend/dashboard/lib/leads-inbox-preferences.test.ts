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
        page: 0,
      }),
    ).toEqual(DEFAULT_LEADS_INBOX_PREFERENCES);
  });

  it("ignores legacy filter fields from older cache entries", () => {
    expect(
      normalizeLeadsInboxPreferences({
        statusFilter: "new",
        qualificationFilter: "qualified",
        contactableFilter: "true",
        sort: "created_at_desc",
        page: 2,
        inboxView: "active",
      }),
    ).toEqual({
      sort: "created_at_desc",
      page: 2,
      inboxView: "active",
    });
  });

  it("migrates lead_score_desc sort to urgency_desc", () => {
    expect(
      normalizeLeadsInboxPreferences({
        sort: "lead_score_desc",
      }).sort,
    ).toBe("urgency_desc");
  });

  it("migrates archived inbox view to contacted", () => {
    expect(
      normalizeLeadsInboxPreferences({
        inboxView: "archived",
      }).inboxView,
    ).toBe("contacted");
  });

  it("persists valid filter selections across reads", () => {
    const preferences = {
      sort: "urgency_desc" as const,
      page: 2,
      inboxView: "contacted" as const,
    };

    setLeadsInboxPreferences(preferences);
    expect(getLeadsInboxPreferences()).toEqual(preferences);
  });
});
