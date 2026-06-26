import {
  LEAD_SORT_OPTIONS,
  QUALIFICATION_STATUSES,
  type LeadSort,
} from "@/lib/lead-qualification";
import {
  getDashboardCache,
  setDashboardCache,
} from "@/lib/dashboard-cache";
import type { LeadStatus, QualificationStatus } from "@/lib/types";
import { LEAD_STATUSES } from "@/lib/types";

export const LEADS_INBOX_PREFERENCES_CACHE_KEY = "leads-inbox-preferences";

export type LeadsInboxView = "active" | "archived";

export type LeadsInboxPreferences = {
  statusFilter: LeadStatus | "";
  qualificationFilter: QualificationStatus | "";
  contactableFilter: "true" | "false" | "";
  sort: LeadSort;
  page: number;
  inboxView: LeadsInboxView;
};

export const DEFAULT_LEADS_INBOX_PREFERENCES: LeadsInboxPreferences = {
  statusFilter: "",
  qualificationFilter: "",
  contactableFilter: "",
  sort: "created_at_desc",
  page: 1,
  inboxView: "active",
};

function isLeadStatus(value: unknown): value is LeadStatus {
  return typeof value === "string" && LEAD_STATUSES.includes(value as LeadStatus);
}

function isQualificationStatus(value: unknown): value is QualificationStatus {
  return (
    typeof value === "string" &&
    QUALIFICATION_STATUSES.includes(value as QualificationStatus)
  );
}

function isContactableFilter(value: unknown): value is "true" | "false" | "" {
  return value === "" || value === "true" || value === "false";
}

function isLeadSort(value: unknown): value is LeadSort {
  return (
    typeof value === "string" && LEAD_SORT_OPTIONS.includes(value as LeadSort)
  );
}

function isInboxView(value: unknown): value is LeadsInboxView {
  return value === "active" || value === "archived";
}

export function normalizeLeadsInboxPreferences(
  raw: unknown,
): LeadsInboxPreferences {
  if (!raw || typeof raw !== "object") {
    return DEFAULT_LEADS_INBOX_PREFERENCES;
  }

  const value = raw as Partial<LeadsInboxPreferences>;
  const statusFilter =
    value.statusFilter === "" || isLeadStatus(value.statusFilter)
      ? (value.statusFilter ?? "")
      : "";
  const qualificationFilter =
    value.qualificationFilter === "" ||
    isQualificationStatus(value.qualificationFilter)
      ? (value.qualificationFilter ?? "")
      : "";
  const contactableFilter = isContactableFilter(value.contactableFilter)
    ? value.contactableFilter
    : "";
  const sort = isLeadSort(value.sort) ? value.sort : "created_at_desc";
  const page =
    typeof value.page === "number" && Number.isInteger(value.page) && value.page > 0
      ? value.page
      : 1;
  const inboxView = isInboxView(value.inboxView) ? value.inboxView : "active";

  return {
    statusFilter,
    qualificationFilter,
    contactableFilter,
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
