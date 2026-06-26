"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { InquiryCard } from "@/components/inquiry-card";
import { InquiryTableActions } from "@/components/inquiry-table-actions";
import { InquirySourceBadge } from "@/components/inquiry-source-badge";
import { StatusBadge } from "@/components/status-badge";
import { AlertBanner } from "@/components/ui/alert-banner";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { fetchLeads, restoreLead, seedDemoData, updateLeadStatus } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import { isDevelopment } from "@/lib/env";
import {
  LEAD_SORT_OPTIONS,
  formatLeadScore,
  isKnownContactMethod,
  type LeadSort,
} from "@/lib/lead-qualification";
import { formatDateTime } from "@/lib/format-datetime";
import {
  DEFAULT_LEADS_INBOX_PREFERENCES,
  getLeadsInboxPreferences,
  setLeadsInboxPreferences,
  type LeadsInboxView,
} from "@/lib/leads-inbox-preferences";
import type { Lead } from "@/lib/types";
import { Link } from "@/i18n/navigation";

function formatDate(value: string, locale: string): string {
  return formatDateTime(value, locale, "medium") ?? "";
}

export function LeadsDashboard() {
  const locale = useLocale();
  const { loading: authLoading, error: authError } = useAuth();
  const t = useTranslations("leads");
  const tCommon = useTranslations("common");
  const tContactMethod = useTranslations("contactMethod");
  const tErrors = useTranslations("errors");
  const errorMessages = useMemo(() => getErrorMessages(tErrors), [tErrors]);
  const initialPreferences = useMemo(() => getLeadsInboxPreferences(), []);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [sort, setSort] = useState<LeadSort>(initialPreferences.sort);
  const [page, setPage] = useState(initialPreferences.page);
  const [inboxView, setInboxView] = useState<LeadsInboxView>(
    initialPreferences.inboxView,
  );
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [contactedSuccessId, setContactedSuccessId] = useState<string | null>(null);
  const [seeding, setSeeding] = useState(false);
  const [restoreSuccessId, setRestoreSuccessId] = useState<string | null>(null);
  const isContactedView = inboxView === "contacted";

  const loadLeads = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLeads({
        page,
        page_size: 20,
        contactable: true,
        sort,
        archived: isContactedView,
      });
      setLeads(Array.isArray(data.items) ? data.items : []);
      setTotalPages(typeof data.total_pages === "number" ? data.total_pages : 1);
      setTotal(typeof data.total === "number" ? data.total : 0);
    } catch (err) {
      setError(formatUserFacingError(err, t("loadFailed"), errorMessages));
    } finally {
      setLoading(false);
    }
  }, [page, sort, isContactedView, t, errorMessages]);

  useEffect(() => {
    if (authLoading) {
      return;
    }
    void loadLeads();
  }, [loadLeads, authLoading]);

  useEffect(() => {
    setLeadsInboxPreferences({
      sort,
      page,
      inboxView,
    });
  }, [sort, page, inboxView]);

  function applyLeadUpdate(updated: Lead) {
    if (!isContactedView && updated.status !== "new") {
      setLeads((current) => current.filter((lead) => lead.id !== updated.id));
      setTotal((current) => Math.max(0, current - 1));
      return;
    }

    setLeads((current) =>
      current.map((lead) => (lead.id === updated.id ? updated : lead)),
    );
  }

  async function handleMarkContacted(leadId: string) {
    setUpdatingId(leadId);
    setError(null);
    setContactedSuccessId(null);
    try {
      const updated = await updateLeadStatus(leadId, "contacted");
      applyLeadUpdate(updated);
      if (updated.status === "contacted") {
        setContactedSuccessId(leadId);
      }
    } catch (err) {
      setError(formatUserFacingError(err, t("updateFailed"), errorMessages));
    } finally {
      setUpdatingId(null);
    }
  }

  async function handleRestoreLead(leadId: string) {
    setUpdatingId(leadId);
    setError(null);
    setRestoreSuccessId(null);
    try {
      await restoreLead(leadId);
      setLeads((current) => current.filter((lead) => lead.id !== leadId));
      setTotal((current) => Math.max(0, current - 1));
      setRestoreSuccessId(leadId);
    } catch (err) {
      setError(formatUserFacingError(err, t("restoreFailed"), errorMessages));
    } finally {
      setUpdatingId(null);
    }
  }

  function handleInboxViewChange(nextView: LeadsInboxView) {
    if (nextView === inboxView) {
      return;
    }
    setInboxView(nextView);
    setPage(1);
    setRestoreSuccessId(null);
    setContactedSuccessId(null);
  }

  async function handleSeedDemoData() {
    setSeeding(true);
    setError(null);
    try {
      setInboxView("active");
      setPage(1);
      setLeadsInboxPreferences(DEFAULT_LEADS_INBOX_PREFERENCES);

      await seedDemoData();

      const data = await fetchLeads({
        page: 1,
        page_size: 20,
        contactable: true,
        sort,
        archived: false,
      });
      setLeads(Array.isArray(data.items) ? data.items : []);
      setTotalPages(typeof data.total_pages === "number" ? data.total_pages : 1);
      setTotal(typeof data.total === "number" ? data.total : 0);
    } catch (err) {
      setError(formatUserFacingError(err, t("seedFailed"), errorMessages));
    } finally {
      setSeeding(false);
    }
  }

  function formatMethod(
    value: Lead["contact_method"],
  ): string {
    if (!isKnownContactMethod(value)) {
      return tCommon("dash");
    }
    return tContactMethod(value);
  }

  const isDataLoading = authLoading || loading;
  const showFirstRunEmpty =
    !isContactedView && !isDataLoading && leads.length === 0;
  const showContactedEmpty =
    isContactedView && !isDataLoading && leads.length === 0;
  const useCardView = !isDataLoading && total > 0 && total <= 10;

  return (
    <div className="stack">
      <PageHeader
        title={isContactedView ? t("contactedTitle") : t("title")}
        description={isContactedView ? t("contactedDescription") : t("description")}
      />
      <div className="inbox-view-toggle" role="tablist" aria-label={t("viewToggleLabel")}>
        <button
          type="button"
          role="tab"
          className={`button secondary${isContactedView ? "" : " is-active"}`}
          aria-selected={!isContactedView}
          onClick={() => handleInboxViewChange("active")}
        >
          {t("viewActive")}
        </button>
        <button
          type="button"
          role="tab"
          className={`button secondary${isContactedView ? " is-active" : ""}`}
          aria-selected={isContactedView}
          onClick={() => handleInboxViewChange("contacted")}
        >
          {t("viewContacted")}
        </button>
      </div>
      <div className="toolbar">
        <div className="toolbar-filters">
          <label className="field-inline">
            <span>{t("sort")}</span>
            <select
              className="select"
              value={sort}
              disabled={isDataLoading}
              onChange={(event) => {
                setPage(1);
                setSort(event.target.value as LeadSort);
              }}
            >
              {LEAD_SORT_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {t(`sortOptions.${option}`)}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="toolbar-actions">
          {isDevelopment && !isContactedView ? (
            <button
              type="button"
              className="button dev"
              disabled={seeding || isDataLoading}
              onClick={() => void handleSeedDemoData()}
            >
              {seeding ? t("creatingDemo") : t("createDemo")}
            </button>
          ) : null}
          <p className="muted">
            {isDataLoading ? tCommon("dash") : t("leadCount", { count: total })}
          </p>
        </div>
      </div>

      {restoreSuccessId ? (
        <AlertBanner variant="success">{t("restoreSuccess")}</AlertBanner>
      ) : null}

      {authError ? <AlertBanner>{authError}</AlertBanner> : null}
      {error ? <AlertBanner>{error}</AlertBanner> : null}

      {isDataLoading ? (
        <div className="card content-loading-panel">
          <LoadingState label={t("loading")} />
        </div>
      ) : null}

      {showFirstRunEmpty ? (
        <EmptyState
          title={t("emptyTitle")}
          description={t("emptyDescription")}
          actionHref="/settings"
          actionLabel={t("emptySetupCta")}
          secondaryActionHref="/demo-chat"
          secondaryActionLabel={t("emptyDemoCta")}
          linkHref="/getting-started"
          linkLabel={t("emptyChecklistLink")}
        />
      ) : null}

      {showContactedEmpty ? (
        <EmptyState
          title={t("emptyContactedTitle")}
          description={t("emptyContactedDescription")}
        />
      ) : null}

      {useCardView ? (
        <div className="inquiry-list">
          {leads.map((lead) => (
            <InquiryCard
              key={lead.id}
              lead={lead}
              createdLabel={formatDate(lead.created_at, locale)}
              statusUpdating={updatingId === lead.id}
              showContactedSuccess={contactedSuccessId === lead.id}
              contactedMode={isContactedView}
              onMarkContacted={() => void handleMarkContacted(lead.id)}
              onRestore={() => void handleRestoreLead(lead.id)}
            />
          ))}
        </div>
      ) : null}

      {!isDataLoading && total > 10 ? (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>{t("tableName")}</th>
                <th>{t("tableSource")}</th>
                <th>{t("tableScore")}</th>
                <th>{t("tableMethod")}</th>
                <th>{t("tablePhone")}</th>
                <th>{t("tableService")}</th>
                <th>{t("tableStatus")}</th>
                <th>{t("tableCreated")}</th>
                <th>{t("tableActions")}</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id}>
                  <td>
                    <Link href={`/leads/${lead.id}`} className="link">
                      {lead.name}
                    </Link>
                  </td>
                  <td>
                    <InquirySourceBadge source={lead.source} />
                  </td>
                  <td>
                    <span className="score-pill">{formatLeadScore(lead.lead_score)}</span>
                  </td>
                  <td>{formatMethod(lead.contact_method)}</td>
                  <td>{lead.phone}</td>
                  <td>{lead.service_requested}</td>
                  <td>
                    <StatusBadge status={lead.status} />
                  </td>
                  <td>{formatDate(lead.created_at, locale)}</td>
                  <td>
                    <InquiryTableActions
                      lead={lead}
                      updating={updatingId === lead.id}
                      contactedMode={isContactedView}
                      onMarkContacted={() => void handleMarkContacted(lead.id)}
                      onRestore={() => void handleRestoreLead(lead.id)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {totalPages > 1 ? (
        <div className="pagination">
          <button
            type="button"
            className="button secondary"
            disabled={page <= 1}
            onClick={() => setPage((current) => current - 1)}
          >
            {t("previous")}
          </button>
          <span className="muted">
            {t("pageOf", { page, total: totalPages })}
          </span>
          <button
            type="button"
            className="button secondary"
            disabled={page >= totalPages}
            onClick={() => setPage((current) => current + 1)}
          >
            {t("next")}
          </button>
        </div>
      ) : null}
    </div>
  );
}
