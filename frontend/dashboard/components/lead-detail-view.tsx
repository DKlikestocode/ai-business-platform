"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { InquirySourceBadge } from "@/components/inquiry-source-badge";
import { FirstWebsiteInquiryMarker } from "@/components/first-website-inquiry-marker";
import { InquiryCallbackActions } from "@/components/inquiry-callback-actions";
import { InquiryContactedIndicator } from "@/components/inquiry-contacted-indicator";
import { InquiryNotificationIndicator } from "@/components/inquiry-notification-indicator";
import { StatusBadge } from "@/components/status-badge";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchLead, restoreLead, updateLeadStatus } from "@/lib/api";
import { formatDateTime } from "@/lib/format-datetime";
import {
  displayName,
  handoffPreviewText,
  hasContactData,
  normalizeEmail,
  normalizePhone,
} from "@/lib/inquiry-handoff";
import { shouldShowFirstWebsiteInquiryMarker } from "@/lib/first-website-inquiry";
import { formatUrgencyLabel } from "@/lib/urgency-level";
import type { Lead } from "@/lib/types";
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
  const [lead, setLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);
  const [showContactedSuccess, setShowContactedSuccess] = useState(false);
  const [restoreSuccess, setRestoreSuccess] = useState(false);

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

  useEffect(() => {
    setShowContactedSuccess(false);
    setRestoreSuccess(false);
  }, [leadId]);

  async function handleRestore() {
    if (!lead) return;
    setUpdating(true);
    setError(null);
    setRestoreSuccess(false);
    try {
      const updated = await restoreLead(lead.id);
      setLead(updated);
      setRestoreSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("restoreFailed"));
    } finally {
      setUpdating(false);
    }
  }

  async function handleMarkContacted() {
    if (!lead) return;
    setUpdating(true);
    setError(null);
    setShowContactedSuccess(false);
    try {
      const updated = await updateLeadStatus(lead.id, "contacted");
      setLead(updated);
      setShowContactedSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("updateFailed"));
    } finally {
      setUpdating(false);
    }
  }

  const phone = lead ? normalizePhone(lead) : null;
  const email = lead ? normalizeEmail(lead) : null;
  const preview = lead
    ? handoffPreviewText(lead, t("noDescription"))
    : t("noDescription");
  const urgencyLabel = lead
    ? formatUrgencyLabel(lead.urgency, (level) => tLeads(`urgencyLevels.${level}`))
    : null;
  const preferredCallback = lead?.preferred_callback_time?.trim() || null;
  const showContactActions = lead ? hasContactData(lead) : false;
  const showFirstWebsiteMarker = lead
    ? shouldShowFirstWebsiteInquiryMarker(lead)
    : false;
  const isContacted = lead ? lead.status !== "new" : false;
  const isNew = lead?.status === "new";

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
            <h2>{t("handoffTitle")}</h2>
            <div className="detail-header-badges">
              {urgencyLabel || preferredCallback ? (
                <div className="inquiry-card-corner-meta inquiry-detail-corner-meta">
                  {urgencyLabel ? (
                    <span className="inquiry-card-corner-item">
                      <span className="inquiry-card-corner-label">{t("howUrgent")}</span>
                      <span className="inquiry-card-corner-value">{urgencyLabel}</span>
                    </span>
                  ) : null}
                  {preferredCallback ? (
                    <span className="inquiry-card-corner-item">
                      <span className="inquiry-card-corner-label">
                        {t("preferredCallback")}
                      </span>
                      <span className="inquiry-card-corner-value">
                        {preferredCallback}
                      </span>
                    </span>
                  ) : null}
                </div>
              ) : null}
              <StatusBadge status={lead.status} />
            </div>
          </div>

          {error ? <div className="alert">{error}</div> : null}
          {restoreSuccess ? (
            <AlertBanner variant="success">{t("restoreSuccess")}</AlertBanner>
          ) : null}
          {isContacted ? (
            <AlertBanner variant="info">
              <div className="stack">
                <p>{t("contactedNotice")}</p>
                <button
                  type="button"
                  className="button"
                  disabled={updating}
                  onClick={() => void handleRestore()}
                >
                  {t("restore")}
                </button>
              </div>
            </AlertBanner>
          ) : null}

          {showFirstWebsiteMarker ? (
            <FirstWebsiteInquiryMarker variant="detail" />
          ) : null}

          <div className="card inquiry-handoff-card">
            <dl className="inquiry-handoff-list">
              <div className="inquiry-handoff-row">
                <dt>{t("who")}</dt>
                <dd className="inquiry-handoff-value">
                  {displayName(lead.name, t("unknownContact"))}
                </dd>
              </div>
              <div className="inquiry-handoff-row">
                <dt>{t("whatAbout")}</dt>
                <dd className="inquiry-handoff-value">{preview}</dd>
              </div>
              <div className="inquiry-handoff-row">
                <dt>{t("howToContact")}</dt>
                <dd>
                  {showContactActions ? (
                    <div className="inquiry-card-contact">
                      {phone ? (
                        <a
                          href={`tel:${phone}`}
                          className="inquiry-card-contact-link"
                        >
                          {phone}
                        </a>
                      ) : null}
                      {email ? (
                        <a
                          href={`mailto:${email}`}
                          className="inquiry-card-contact-link"
                        >
                          {email}
                        </a>
                      ) : null}
                    </div>
                  ) : (
                    <span className="inquiry-handoff-missing-contact">
                      {t("missingContact")}
                    </span>
                  )}
                </dd>
              </div>
              <div className="inquiry-handoff-row">
                <dt>{t("origin")}</dt>
                <dd>
                  <InquirySourceBadge source={lead.source} />
                </dd>
              </div>
              <div className="inquiry-handoff-row">
                <dt>{t("notificationLabel")}</dt>
                <dd>
                  <InquiryNotificationIndicator
                    notificationSentAt={lead.notification_sent_at}
                    variant="detail"
                  />
                </dd>
              </div>
              {lead.contacted_at ? (
                <div className="inquiry-handoff-row">
                  <dt>{t("contactedAtLabel")}</dt>
                  <dd>
                    <InquiryContactedIndicator
                      contactedAt={lead.contacted_at}
                      variant="detail"
                    />
                  </dd>
                </div>
              ) : null}
            </dl>

            {isNew ? (
              <InquiryCallbackActions
                phone={phone}
                email={email}
                status={lead.status}
                updating={updating}
                showContactedSuccess={showContactedSuccess}
                onMarkContacted={() => void handleMarkContacted()}
              />
            ) : null}
          </div>

          <details className="card inquiry-handoff-more">
            <summary className="inquiry-handoff-more-summary">
              {t("moreDetails")}
            </summary>
            <dl className="detail-list inquiry-handoff-more-list">
              <DetailRow label={t("location")} value={lead.location} />
              <DetailRow label={t("company")} value={lead.company} />
              <DetailRow
                label={t("created")}
                value={formatDate(lead.created_at, locale)}
              />
              {lead.service_requested?.trim() &&
              lead.service_requested.trim() !== preview ? (
                <DetailRow
                  label={t("serviceRequested")}
                  value={lead.service_requested}
                />
              ) : null}
              {lead.description?.trim() &&
              lead.description.trim() !== preview ? (
                <DetailRow
                  label={t("description")}
                  value={lead.description}
                />
              ) : null}
              {lead.summary?.trim() && lead.summary.trim() !== preview ? (
                <DetailRow label={t("summary")} value={lead.summary} />
              ) : null}
            </dl>
          </details>
        </>
      ) : null}
    </div>
  );
}
