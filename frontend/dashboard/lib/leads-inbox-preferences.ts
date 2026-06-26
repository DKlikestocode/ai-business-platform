import {
  getDashboardCache,
  setDashboardCache,
} from "@/lib/dashboard-cache";
import type { LeadStatus } from "@/lib/types";
import { LEAD_STATUSES } from "@/lib/types";

export const LEADS_INBOX_PREFERENCES_CACHE_KEY = "leads-inbox-preferences";

export type LeadsInboxView = "active" | "contacted";

export type LeadsInboxPreferences = {
  statusFilter: LeadStatus | "";
  page: number;
  inboxView: LeadsInboxView;
};

export const DEFAULT_LEADS_INBOX_PREFERENCES: LeadsInboxPreferences = {
  statusFilter: "",
  page: 1,
  inboxView: "active",
};

function isLeadStatus(value: unknown): value is LeadStatus {
  return typeof value === "string" && LEAD_STATUSES.includes(value as LeadStatus);
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
  const statusFilter =
    value.statusFilter === "" || isLeadStatus(value.statusFilter)
      ? (value.statusFilter ?? "")
      : "";
  const page =
    typeof value.page === "number" && Number.isInteger(value.page) && value.page > 0
      ? value.page
      : 1;
  const inboxView = migrateInboxView(value.inboxView);

  return {
    statusFilter,
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
