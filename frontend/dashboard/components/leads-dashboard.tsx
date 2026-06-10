"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
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
import { isDevelopment } from "@/lib/env";
import {
  LEAD_SORT_OPTIONS,
  QUALIFICATION_STATUSES,
  QUALIFICATION_LABELS,
  formatContactMethod,
  formatLeadScore,
} from "@/lib/lead-qualification";
import type { LeadSort } from "@/lib/lead-qualification";
import type { Lead, LeadStatus, QualificationStatus } from "@/lib/types";
import { LEAD_STATUSES, STATUS_LABELS } from "@/lib/types";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function LeadsDashboard() {
  const { loading: authLoading, error: authError } = useAuth();
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
      setError(formatUserFacingError(err, "Failed to load leads."));
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, qualificationFilter, contactableFilter, sort]);

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
      setError(formatUserFacingError(err, "Failed to update lead status."));
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
      setError(formatUserFacingError(err, "Failed to create demo leads."));
    } finally {
      setSeeding(false);
    }
  }

  return (
    <div className="stack">
      <PageHeader
        title="Leads"
        description="Review, qualify, and update inbound customer leads."
      />
      <div className="toolbar">
        <div className="toolbar-filters">
          <label className="field-inline">
            <span>Status</span>
            <select
              className="select"
              value={statusFilter}
              onChange={(event) => {
                setPage(1);
                setStatusFilter(event.target.value as LeadStatus | "");
              }}
            >
              <option value="">All statuses</option>
              {LEAD_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {STATUS_LABELS[status]}
                </option>
              ))}
            </select>
          </label>
          <label className="field-inline">
            <span>Qualification</span>
            <select
              className="select"
              value={qualificationFilter}
              onChange={(event) => {
                setPage(1);
                setQualificationFilter(
                  event.target.value as QualificationStatus | "",
                );
              }}
            >
              <option value="">All qualifications</option>
              {QUALIFICATION_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {QUALIFICATION_LABELS[status]}
                </option>
              ))}
            </select>
          </label>
          <label className="field-inline">
            <span>Contactable</span>
            <select
              className="select"
              value={contactableFilter}
              onChange={(event) => {
                setPage(1);
                setContactableFilter(
                  event.target.value as "true" | "false" | "",
                );
              }}
            >
              <option value="">All</option>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </label>
          <label className="field-inline">
            <span>Sort</span>
            <select
              className="select"
              value={sort}
              onChange={(event) => {
                setPage(1);
                setSort(event.target.value as LeadSort);
              }}
            >
              {LEAD_SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
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
              disabled={seeding || authLoading}
              onClick={() => void handleSeedDemoData()}
            >
              {seeding ? "Creating demo leads..." : "Create demo leads"}
            </button>
          ) : null}
          <p className="muted">{total} lead{total === 1 ? "" : "s"}</p>
        </div>
      </div>

      {seedMessage ? <AlertBanner variant="success">{seedMessage}</AlertBanner> : null}

      {authError ? <AlertBanner>{authError}</AlertBanner> : null}
      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {authLoading || loading ? <LoadingState label="Loading leads..." /> : null}

      {!authLoading && !loading && leads.length === 0 ? (
        <EmptyState
          title="No leads yet"
          description="Install the website widget or send a test message from Demo Chat. Qualified and contactable leads will appear here."
          actionHref="/getting-started"
          actionLabel="View setup checklist"
        />
      ) : null}

      {!authLoading && !loading && leads.length > 0 ? (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Score</th>
                <th>Qualification</th>
                <th>Contactable</th>
                <th>Method</th>
                <th>Phone</th>
                <th>Service</th>
                <th>Status</th>
                <th>Created</th>
                <th>Update</th>
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
                  <td>{formatContactMethod(lead.contact_method)}</td>
                  <td>{lead.phone}</td>
                  <td>{lead.service_requested}</td>
                  <td>
                    <StatusBadge status={lead.status} />
                  </td>
                  <td>{formatDate(lead.created_at)}</td>
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
            Previous
          </button>
          <span className="muted">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            className="button secondary"
            disabled={page >= totalPages}
            onClick={() => setPage((current) => current + 1)}
          >
            Next
          </button>
        </div>
      ) : null}
    </div>
  );
}
