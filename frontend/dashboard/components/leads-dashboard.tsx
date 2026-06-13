"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { InquiryCard } from "@/components/inquiry-card";
import { ContactableBadge } from "@/components/contactable-badge";
import { QualificationBadge } from "@/components/qualification-badge";
import { StatusBadge } from "@/components/status-badge";
import { StatusSelect } from "@/components/status-select";
import { AlertBanner } from "@/components/ui/alert-banner";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { fetchLeads, seedDemoData, updateLeadStatus } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import { isDevelopment } from "@/lib/env";
import {
  LEAD_SORT_OPTIONS,
  QUALIFICATION_STATUSES,
  formatLeadScore,
  isKnownContactMethod,
} from "@/lib/lead-qualification";
import type { LeadSort } from "@/lib/lead-qualification";
import type { Lead, LeadStatus, QualificationStatus } from "@/lib/types";
import { LEAD_STATUSES } from "@/lib/types";
import { Link } from "@/i18n/navigation";

function formatDate(value: string, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function LeadsDashboard() {
  const locale = useLocale();
  const { loading: authLoading, error: authError } = useAuth();
  const t = useTranslations("leads");
  const tCommon = useTranslations("common");
  const tQualification = useTranslations("qualification");
  const tContactMethod = useTranslations("contactMethod");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [statusFilter, setStatusFilter] = useState<LeadStatus | "">("");
  const [qualificationFilter, setQualificationFilter] = useState<
    QualificationStatus | ""
  >("");
  const [contactableFilter, setContactableFilter] = useState<
    "true" | "false" | ""
  >("");
  const [sort, setSort] = useState<LeadSort>("created_at_desc");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [seeding, setSeeding] = useState(false);
  const [seedMessage, setSeedMessage] = useState<string | null>(null);

  const loadLeads = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLeads({
        page,
        page_size: 20,
        status: statusFilter,
        qualification_status: qualificationFilter,
        contactable:
          contactableFilter === ""
            ? ""
            : contactableFilter === "true",
        sort,
      });
      setLeads(data.items);
      setTotalPages(data.total_pages);
      setTotal(data.total);
    } catch (err) {
      setError(formatUserFacingError(err, t("loadFailed"), errorMessages));
    } finally {
      setLoading(false);
    }
  }, [
    page,
    statusFilter,
    qualificationFilter,
    contactableFilter,
    sort,
    t,
    errorMessages,
  ]);

  useEffect(() => {
    if (authLoading) {
      return;
    }
    void loadLeads();
  }, [loadLeads, authLoading]);

  async function handleStatusChange(leadId: string, status: LeadStatus) {
    setUpdatingId(leadId);
    setError(null);
    try {
      const updated = await updateLeadStatus(leadId, status);
      setLeads((current) =>
        current.map((lead) => (lead.id === leadId ? updated : lead)),
      );
    } catch (err) {
      setError(formatUserFacingError(err, t("updateFailed"), errorMessages));
    } finally {
      setUpdatingId(null);
    }
  }

  async function handleSeedDemoData() {
    setSeeding(true);
    setError(null);
    setSeedMessage(null);
    try {
      const result = await seedDemoData();
      setSeedMessage(result.message);
      setPage(1);
      await loadLeads();
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

  const hasActiveFilters = Boolean(
    statusFilter || qualificationFilter || contactableFilter,
  );
  const isDataLoading = authLoading || loading;
  const showFirstRunEmpty =
    !isDataLoading && leads.length === 0 && !hasActiveFilters;
  const useCardView = !isDataLoading && leads.length > 0 && leads.length <= 10;

  return (
    <div className="stack">
      <PageHeader title={t("title")} description={t("description")} />
      <div className="toolbar">
        <div className="toolbar-filters">
          <label className="field-inline">
            <span>{t("status")}</span>
            <select
              className="select"
              value={statusFilter}
              disabled={isDataLoading}
              onChange={(event) => {
                setPage(1);
                setStatusFilter(event.target.value as LeadStatus | "");
              }}
            >
              <option value="">{t("allStatuses")}</option>
              {LEAD_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {t(`statuses.${status}`)}
                </option>
              ))}
            </select>
          </label>
          <label className="field-inline">
            <span>{t("qualification")}</span>
            <select
              className="select"
              value={qualificationFilter}
              disabled={isDataLoading}
              onChange={(event) => {
                setPage(1);
                setQualificationFilter(
                  event.target.value as QualificationStatus | "",
                );
              }}
            >
              <option value="">{t("allQualifications")}</option>
              {QUALIFICATION_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {tQualification(status)}
                </option>
              ))}
            </select>
          </label>
          <label className="field-inline">
            <span>{t("contactable")}</span>
            <select
              className="select"
              value={contactableFilter}
              disabled={isDataLoading}
              onChange={(event) => {
                setPage(1);
                setContactableFilter(
                  event.target.value as "true" | "false" | "",
                );
              }}
            >
              <option value="">{t("all")}</option>
              <option value="true">{tCommon("yes")}</option>
              <option value="false">{tCommon("no")}</option>
            </select>
          </label>
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
          {isDevelopment ? (
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

      {seedMessage ? <AlertBanner variant="success">{seedMessage}</AlertBanner> : null}

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

      {!isDataLoading && leads.length === 0 && hasActiveFilters ? (
        <p className="muted">{t("filterEmptyDescription")}</p>
      ) : null}

      {useCardView ? (
        <div className="inquiry-list">
          {leads.map((lead) => (
            <InquiryCard
              key={lead.id}
              lead={lead}
              createdLabel={formatDate(lead.created_at, locale)}
              statusUpdating={updatingId === lead.id}
              onStatusChange={(status) => void handleStatusChange(lead.id, status)}
            />
          ))}
        </div>
      ) : null}

      {!isDataLoading && leads.length > 10 ? (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>{t("tableName")}</th>
                <th>{t("tableScore")}</th>
                <th>{t("tableQualification")}</th>
                <th>{t("tableContactable")}</th>
                <th>{t("tableMethod")}</th>
                <th>{t("tablePhone")}</th>
                <th>{t("tableService")}</th>
                <th>{t("tableStatus")}</th>
                <th>{t("tableCreated")}</th>
                <th>{t("tableUpdate")}</th>
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
                    <span className="score-pill">{formatLeadScore(lead.lead_score)}</span>
                  </td>
                  <td>
                    <QualificationBadge status={lead.qualification_status} />
                  </td>
                  <td>
                    <ContactableBadge contactable={lead.contactable} />
                  </td>
                  <td>{formatMethod(lead.contact_method)}</td>
                  <td>{lead.phone}</td>
                  <td>{lead.service_requested}</td>
                  <td>
                    <StatusBadge status={lead.status} />
                  </td>
                  <td>{formatDate(lead.created_at, locale)}</td>
                  <td>
                    <StatusSelect
                      value={lead.status}
                      disabled={updatingId === lead.id}
                      onChange={(status) => void handleStatusChange(lead.id, status)}
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
