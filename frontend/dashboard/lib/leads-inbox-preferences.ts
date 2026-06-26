import {
  getDashboardCache,
  setDashboardCache,
} from "@/lib/dashboard-cache";
import {
  LEAD_SORT_OPTIONS,
  type LeadSort,
} from "@/lib/lead-qualification";

export const LEADS_INBOX_PREFERENCES_CACHE_KEY = "leads-inbox-preferences";

export type LeadsInboxView = "active" | "contacted";

export type LeadsInboxPreferences = {
  sort: LeadSort;
  page: number;
  inboxView: LeadsInboxView;
};

export const DEFAULT_LEADS_INBOX_PREFERENCES: LeadsInboxPreferences = {
  sort: "urgency_desc",
  page: 1,
  inboxView: "active",
};

function isLeadSort(value: unknown): value is LeadSort {
  return (
    typeof value === "string" && LEAD_SORT_OPTIONS.includes(value as LeadSort)
  );
}

function migrateSort(value: unknown): LeadSort {
  if (value === "lead_score_desc") {
    return "urgency_desc";
  }
  return isLeadSort(value) ? value : "urgency_desc";
}

function migrateInboxView(value: unknown): LeadsInboxView {
  if (value === "contacted" || value === "active") {
    return value;
  }
  if (value === "archived") {
    return "contacted";
  }
  return "active";
}

export function normalizeLeadsInboxPreferences(
  raw: unknown,
): LeadsInboxPreferences {
  if (!raw || typeof raw !== "object") {
    return DEFAULT_LEADS_INBOX_PREFERENCES;
  }

  const value = raw as Partial<LeadsInboxPreferences> & Record<string, unknown>;
  const page =
    typeof value.page === "number" && Number.isInteger(value.page) && value.page > 0
      ? value.page
      : 1;
  const inboxView = migrateInboxView(value.inboxView);
  const sort = migrateSort(value.sort);

  return {
    sort,
    page,
    inboxView,
  };
}

export function getLeadsInboxPreferences(): LeadsInboxPreferences {
  return normalizeLeadsInboxPreferences(
    getDashboardCache<unknown>(LEADS_INBOX_PREFERENCES_CACHE_KEY),
  );
}

export function setLeadsInboxPreferences(preferences: LeadsInboxPreferences): void {
  setDashboardCache(LEADS_INBOX_PREFERENCES_CACHE_KEY, preferences);
}
