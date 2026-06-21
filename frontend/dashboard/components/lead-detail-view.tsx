"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { ContactableBadge } from "@/components/contactable-badge";
import { InquirySourceBadge } from "@/components/inquiry-source-badge";
import { QualificationBadge } from "@/components/qualification-badge";
import { StatusBadge } from "@/components/status-badge";
import { StatusSelect } from "@/components/status-select";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchLead, updateLeadStatus } from "@/lib/api";
import {
  formatLeadScore,
  isKnownContactMethod,
} from "@/lib/lead-qualification";
import { formatDateTime } from "@/lib/format-datetime";
import type { Lead, LeadStatus } from "@/lib/types";
import { Link } from "@/i18n/navigation";

function formatDate(value: string, locale: string): string {
  return formatDateTime(value, locale, "full") ?? "";
}

function DetailRow({ label, value }: { label: string; value: string | null }) {
  const tCommon = useTranslations("common");

  return (
    <div className="detail-row">
      <dt>{label}</dt>
      <dd>{value || tCommon("dash")}</dd>
    </div>
  );
}

export function LeadDetailView() {
  const params = useParams<{ id: string }>();
  const leadId = Array.isArray(params.id) ? params.id[0] : params.id;
  const locale = useLocale();
  const t = useTranslations("leadDetail");
  const tLeads = useTranslations("leads");
  const tCommon = useTranslations("common");
  const tContactMethod = useTranslations("contactMethod");
  const [lead, setLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);

  const loadLead = useCallback(async () => {
    if (!leadId) {
      setLead(null);
      setError(t("notFound"));
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await fetchLead(leadId);
      setLead(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("loadFailed"));
    } finally {
      setLoading(false);
    }
  }, [leadId, t]);

  useEffect(() => {
    void loadLead();
  }, [loadLead]);

  async function handleStatusChange(status: LeadStatus) {
    if (!lead) return;
    setUpdating(true);
    setError(null);
    try {
      const updated = await updateLeadStatus(lead.id, status);
      setLead(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("updateFailed"));
    } finally {
      setUpdating(false);
    }
  }

  function formatMethod(value: Lead["contact_method"]): string | null {
    if (!isKnownContactMethod(value)) {
      return null;
    }
    return tContactMethod(value);
  }

  return (
    <div className="stack">
      <Link href="/leads" className="back-link">
        {t("backToLeads")}
      </Link>

      {loading ? (
        <>
          <div className="card content-loading-panel">
            <LoadingState label={t("loading")} />
          </div>
          <div className="card content-loading-panel" aria-hidden="true" />
        </>
      ) : null}

      {!loading && error && !lead ? (
        <div className="alert">{error}</div>
      ) : null}

      {!loading && !lead ? (
        <div className="empty-state">{t("notFound")}</div>
      ) : null}

      {!loading && lead ? (
        <>
          <div className="detail-header">
            <div>
              <h2>{lead.name}</h2>
              <p className="muted">
                {t("leadId")} {lead.id}
              </p>
            </div>
            <div className="detail-header-badges">
              <InquirySourceBadge source={lead.source} />
              <StatusBadge status={lead.status} />
            </div>
          </div>

          {error ? <div className="alert">{error}</div> : null}

          <div className="card">
            <h3 className="card-title">{t("qualification")}</h3>
            <dl className="detail-list">
              <div className="detail-row">
                <dt>{t("leadScore")}</dt>
                <dd>
                  <span className="score-pill">
                    {formatLeadScore(lead.lead_score)}
                  </span>
                </dd>
              </div>
              <div className="detail-row">
                <dt>{t("qualificationStatus")}</dt>
                <dd>
                  <QualificationBadge status={lead.qualification_status} />
                </dd>
              </div>
              <div className="detail-row">
                <dt>{t("contactable")}</dt>
                <dd>
                  <ContactableBadge contactable={lead.contactable} />
                </dd>
              </div>
              <DetailRow
                label={t("contactMethod")}
                value={formatMethod(lead.contact_method)}
              />
              <DetailRow
                label={t("notificationSent")}
                value={
                  lead.notification_sent_at
                    ? formatDate(lead.notification_sent_at, locale)
                    : null
                }
              />
            </dl>
          </div>

          <div className="card">
            <h3 className="card-title">{t("details")}</h3>
            <dl className="detail-list">
              <DetailRow label={tLeads("tablePhone")} value={lead.phone} />
              <DetailRow label={tCommon("email")} value={lead.email} />
              <DetailRow label={t("company")} value={lead.company} />
              <DetailRow label={t("location")} value={lead.location} />
              <DetailRow
                label={t("serviceRequested")}
                value={lead.service_requested}
              />
              <DetailRow label={t("description")} value={lead.description} />
              <DetailRow label={t("urgency")} value={lead.urgency} />
              <DetailRow
                label={t("preferredCallback")}
                value={lead.preferred_callback_time}
              />
              <div className="detail-row">
                <dt>{t("source")}</dt>
                <dd>
                  <InquirySourceBadge source={lead.source} />
                </dd>
              </div>
              <DetailRow
                label={t("conversationId")}
                value={lead.conversation_id}
              />
              <DetailRow
                label={t("created")}
                value={formatDate(lead.created_at, locale)}
              />
              <DetailRow label={t("summary")} value={lead.summary} />
            </dl>
          </div>

          <div className="card">
            <label className="field-block">
              <span>{t("updateStatus")}</span>
              <StatusSelect
                value={lead.status}
                disabled={updating}
                onChange={(status) => void handleStatusChange(status)}
              />
            </label>
          </div>
        </>
      ) : null}
    </div>
  );
}
