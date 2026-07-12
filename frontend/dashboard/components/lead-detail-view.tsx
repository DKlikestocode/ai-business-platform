"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { InquiryKindBadge } from "@/components/inquiry-kind-badge";
import { InquirySourceBadge } from "@/components/inquiry-source-badge";
import { FirstWebsiteInquiryMarker } from "@/components/first-website-inquiry-marker";
import { InquiryCallbackActions } from "@/components/inquiry-callback-actions";
import { InquiryContactedIndicator } from "@/components/inquiry-contacted-indicator";
import { InquiryCustomerConfirmationIndicator } from "@/components/inquiry-customer-confirmation-indicator";
import { InquiryNotificationIndicator } from "@/components/inquiry-notification-indicator";
import { ServiceAreaStatusBadge } from "@/components/service-area-status-badge";
import { StatusBadge } from "@/components/status-badge";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchLead, deleteLead, restoreLead, updateLeadStatus } from "@/lib/api";
import {
  COMPANY_SETTINGS_CACHE_KEY,
  getDashboardCache,
  loadCachedCompanySettings,
} from "@/lib/dashboard-cache";
import { formatDateTime } from "@/lib/format-datetime";
import {
  displayName,
  handoffPreviewText,
  hasContactData,
  normalizeEmail,
  normalizePhone,
} from "@/lib/inquiry-handoff";
import { shouldShowFirstWebsiteInquiryMarker } from "@/lib/first-website-inquiry";
import { shouldShowCustomerConfirmationIndicator } from "@/lib/inquiry-customer-confirmation";
import { formatUrgencyLabel } from "@/lib/urgency-level";
import type { CompanySettings, Lead } from "@/lib/types";
import { Link, useRouter } from "@/i18n/navigation";

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
  const router = useRouter();
  const [lead, setLead] = useState<Lead | null>(null);
  const [settings, setSettings] = useState<CompanySettings | null>(() =>
    getDashboardCache<CompanySettings>(COMPANY_SETTINGS_CACHE_KEY),
  );
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
    void loadCachedCompanySettings(setSettings);
  }, []);

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

  async function handleDelete() {
    if (!lead) return;
    if (!window.confirm(t("deleteConfirm"))) {
      return;
    }

    setUpdating(true);
    setError(null);
    try {
      await deleteLead(lead.id);
      router.push("/leads");
    } catch (err) {
      setError(err instanceof Error ? err.message : t("deleteFailed"));
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
  const showCustomerConfirmation = lead
    ? shouldShowCustomerConfirmationIndicator(
        settings?.send_customer_confirmation ?? false,
        lead.customer_confirmation_sent_at,
      )
    : false;
  const isContacted = lead ? lead.status !== "new" : false;
  const isNew = lead?.status === "new";
  const hasUrgencySection = Boolean(urgencyLabel || preferredCallback);
  const serviceLine = lead?.service_requested?.trim() || null;

  return (
    <div className={`stack lead-detail${showContactActions ? " lead-detail--has-sticky-contact" : ""}`}>
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
        <div className="content-fade-in lead-detail-body">
          <div className="detail-header lead-detail-header">
            <h2 className="lead-detail-page-title">{t("handoffTitle")}</h2>
            <div className="detail-header-badges lead-detail-badges">
              <InquiryKindBadge inquiryKind={lead.inquiry_kind} />
              <ServiceAreaStatusBadge
                status={lead.service_area_status}
                distanceKm={lead.service_area_distance_km}
              />
              <StatusBadge status={lead.status} />
            </div>
          </div>

          {error ? <div className="alert">{error}</div> : null}
          {restoreSuccess ? (
            <div className="success-fade-in">
              <AlertBanner variant="success">{t("restoreSuccess")}</AlertBanner>
            </div>
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

          <section className="card lead-detail-hero" aria-labelledby="lead-detail-who">
            <p id="lead-detail-who" className="lead-detail-section-label">
              {t("who")}
            </p>
            <h3 className="lead-detail-hero-name">
              {displayName(lead.name, t("unknownContact"))}
            </h3>
          </section>

          <section className="card lead-detail-section-card" aria-labelledby="lead-detail-anliegen">
            <h3 id="lead-detail-anliegen" className="lead-detail-section-title">
              {t("whatAbout")}
            </h3>
            {serviceLine ? (
              <p className="lead-detail-service">{serviceLine}</p>
            ) : null}
            <p className="lead-detail-anliegen">{preview}</p>
          </section>

          {hasUrgencySection ? (
            <section
              className="card lead-detail-section-card lead-detail-urgency-card"
              aria-labelledby="lead-detail-urgency"
            >
              <h3 id="lead-detail-urgency" className="lead-detail-section-title">
                {t("howUrgent")}
              </h3>
              <div className="lead-detail-urgency-content">
                {urgencyLabel ? (
                  <span className="lead-detail-urgency-value">{urgencyLabel}</span>
                ) : null}
                {preferredCallback ? (
                  <p className="lead-detail-callback muted">
                    <span className="lead-detail-callback-label">
                      {t("preferredCallback")}
                    </span>
                    <span className="lead-detail-callback-value">{preferredCallback}</span>
                  </p>
                ) : null}
              </div>
            </section>
          ) : null}

          <section
            className="card lead-detail-section-card lead-detail-contact-section"
            aria-labelledby="lead-detail-contact"
          >
            <h3 id="lead-detail-contact" className="lead-detail-section-title">
              {t("howToContact")}
            </h3>
            {isNew ? (
              <InquiryCallbackActions
                phone={phone}
                email={email}
                status={lead.status}
                updating={updating}
                showContactedSuccess={showContactedSuccess}
                onMarkContacted={() => void handleMarkContacted()}
              />
            ) : showContactActions ? (
              <div className="lead-detail-contact-actions">
                {phone ? (
                  <a
                    href={`tel:${phone}`}
                    className="button lead-detail-contact-btn lead-detail-contact-btn--call"
                    aria-label={`${t("call")} ${phone}`}
                  >
                    {t("call")}
                  </a>
                ) : null}
                {email ? (
                  <a
                    href={`mailto:${email}`}
                    className="button secondary lead-detail-contact-btn"
                    aria-label={`${t("emailAction")} ${email}`}
                  >
                    {t("emailAction")}
                  </a>
                ) : null}
              </div>
            ) : (
              <p className="inquiry-handoff-missing-contact">{t("missingContact")}</p>
            )}
          </section>

          <section
            className="card lead-detail-section-card lead-detail-meta-card"
            aria-labelledby="lead-detail-meta"
          >
            <h3 id="lead-detail-meta" className="lead-detail-section-title lead-detail-meta-title">
              {t("moreDetails")}
            </h3>
            <dl className="lead-detail-meta-list">
              <div className="lead-detail-meta-row">
                <dt>{t("origin")}</dt>
                <dd>
                  <InquirySourceBadge source={lead.source} />
                </dd>
              </div>
              <div className="lead-detail-meta-row">
                <dt>{t("notificationLabel")}</dt>
                <dd>
                  <InquiryNotificationIndicator
                    notificationSentAt={lead.notification_sent_at}
                    variant="detail"
                  />
                </dd>
              </div>
              {showCustomerConfirmation ? (
                <div className="lead-detail-meta-row">
                  <dt>{t("customerConfirmationLabel")}</dt>
                  <dd>
                    <InquiryCustomerConfirmationIndicator
                      customerConfirmationSentAt={lead.customer_confirmation_sent_at}
                      variant="detail"
                    />
                  </dd>
                </div>
              ) : null}
              {lead.contacted_at ? (
                <div className="lead-detail-meta-row">
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
          </section>

          <details className="card inquiry-handoff-more">
            <summary className="inquiry-handoff-more-summary">
              {t("moreDetails")}
            </summary>
            <dl className="detail-list inquiry-handoff-more-list">
              <DetailRow label={t("postalCode")} value={lead.postal_code} />
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

          <div className="inquiry-card-actions inquiry-detail-footer">
            <button
              type="button"
              className="inquiry-card-delete"
              disabled={updating}
              aria-label={t("deleteAria")}
              onClick={() => void handleDelete()}
            >
              {t("delete")}
            </button>
          </div>

          {showContactActions ? (
            <div
              className="lead-detail-sticky-contact"
              role="toolbar"
              aria-label={t("contactNow")}
            >
              {phone ? (
                <a
                  href={`tel:${phone}`}
                  className="button lead-detail-sticky-btn lead-detail-sticky-btn--call"
                  aria-label={`${t("call")} ${phone}`}
                >
                  {t("call")}
                </a>
              ) : null}
              {email ? (
                <a
                  href={`mailto:${email}`}
                  className="button secondary lead-detail-sticky-btn"
                  aria-label={`${t("emailAction")} ${email}`}
                >
                  {t("emailAction")}
                </a>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
