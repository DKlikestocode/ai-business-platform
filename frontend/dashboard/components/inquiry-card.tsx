"use client";

import { useTranslations } from "next-intl";

import { InquiryKindBadge } from "@/components/inquiry-kind-badge";
import { StatusBadge } from "@/components/status-badge";
import { FirstWebsiteInquiryMarker } from "@/components/first-website-inquiry-marker";
import { InquiryCallbackActions } from "@/components/inquiry-callback-actions";
import { InquiryContactedIndicator } from "@/components/inquiry-contacted-indicator";
import { InquiryNotificationIndicator } from "@/components/inquiry-notification-indicator";
import { InquirySourceBadge } from "@/components/inquiry-source-badge";
import { ServiceAreaStatusBadge } from "@/components/service-area-status-badge";
import { Link } from "@/i18n/navigation";
import {
  displayName,
  handoffPreviewText,
  normalizeEmail,
  normalizePhone,
} from "@/lib/inquiry-handoff";
import { shouldShowFirstWebsiteInquiryMarker } from "@/lib/first-website-inquiry";
import { formatUrgencyLabel } from "@/lib/urgency-level";
import type { Lead } from "@/lib/types";

interface InquiryCardProps {
  lead: Lead;
  createdLabel: string;
  statusUpdating: boolean;
  showContactedSuccess: boolean;
  contactedMode?: boolean;
  onMarkContacted: () => void;
  onRestore?: () => void;
  onDelete?: () => void;
}

export function InquiryCard({
  lead,
  createdLabel,
  statusUpdating,
  showContactedSuccess,
  contactedMode = false,
  onMarkContacted,
  onRestore,
  onDelete,
}: InquiryCardProps) {
  const t = useTranslations("leads");
  const phone = normalizePhone(lead);
  const email = normalizeEmail(lead);
  const urgencyLabel = formatUrgencyLabel(lead.urgency, (level) =>
    t(`urgencyLevels.${level}`),
  );
  const preferredCallback = lead.preferred_callback_time?.trim() || null;
  const preview = handoffPreviewText(lead, t("noDescription"));
  const showFirstWebsiteMarker = shouldShowFirstWebsiteInquiryMarker(lead);
  const hasCornerMeta = Boolean(urgencyLabel || preferredCallback);

  return (
    <article className="inquiry-card card">
      {showFirstWebsiteMarker ? <FirstWebsiteInquiryMarker /> : null}
      <div className="inquiry-card-header">
        <div className="inquiry-card-intro">
          <h3 className="inquiry-card-name">
            <Link href={`/leads/${lead.id}`} className="link">
              {displayName(lead.name, t("unknownContact"))}
            </Link>
          </h3>
          {lead.service_requested ? (
            <p className="inquiry-card-service">{lead.service_requested}</p>
          ) : null}
        </div>
        <div className="inquiry-card-meta">
          {hasCornerMeta ? (
            <div className="inquiry-card-corner-meta">
              {urgencyLabel ? (
                <span className="inquiry-card-corner-item">
                  <span className="inquiry-card-corner-label">{t("urgency")}</span>
                  <span className="inquiry-card-corner-value">{urgencyLabel}</span>
                </span>
              ) : null}
              {preferredCallback ? (
                <span className="inquiry-card-corner-item">
                  <span className="inquiry-card-corner-label">
                    {t("preferredCallback")}
                  </span>
                  <span className="inquiry-card-corner-value">{preferredCallback}</span>
                </span>
              ) : null}
            </div>
          ) : null}
          <InquirySourceBadge source={lead.source} />
          <InquiryKindBadge inquiryKind={lead.inquiry_kind} />
          <ServiceAreaStatusBadge
            status={lead.service_area_status}
            distanceKm={lead.service_area_distance_km}
          />
          <StatusBadge status={lead.status} />
          <time className="inquiry-card-date muted" dateTime={lead.created_at}>
            {createdLabel}
          </time>
        </div>
      </div>

      <InquiryNotificationIndicator
        notificationSentAt={lead.notification_sent_at}
      />

      <InquiryContactedIndicator contactedAt={lead.contacted_at} />

      <p className="inquiry-card-preview">{preview}</p>

      {phone || email ? (
        <div className="inquiry-card-contact">
          {phone ? (
            <a href={`tel:${phone}`} className="inquiry-card-contact-link">
              {phone}
            </a>
          ) : null}
          {email ? (
            <a href={`mailto:${email}`} className="inquiry-card-contact-link">
              {email}
            </a>
          ) : null}
        </div>
      ) : null}

      {!contactedMode ? (
        <InquiryCallbackActions
          phone={phone}
          email={email}
          status={lead.status}
          updating={statusUpdating}
          showContactedSuccess={showContactedSuccess}
          onMarkContacted={onMarkContacted}
        />
      ) : null}

      <div className="inquiry-card-actions">
        <Link href={`/leads/${lead.id}`} className="button secondary">
          {t("openDetails")}
        </Link>
        {contactedMode && onRestore ? (
          <button
            type="button"
            className="button"
            disabled={statusUpdating}
            onClick={onRestore}
          >
            {t("restore")}
          </button>
        ) : null}
        {onDelete ? (
          <button
            type="button"
            className="inquiry-card-delete"
            disabled={statusUpdating}
            aria-label={t("deleteAria")}
            onClick={onDelete}
          >
            {t("delete")}
          </button>
        ) : null}
      </div>
    </article>
  );
}
