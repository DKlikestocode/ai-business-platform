"use client";

import { useTranslations } from "next-intl";

import { StatusBadge } from "@/components/status-badge";
import { FirstWebsiteInquiryMarker } from "@/components/first-website-inquiry-marker";
import { InquirySourceBadge } from "@/components/inquiry-source-badge";
import { StatusSelect } from "@/components/status-select";
import { Link } from "@/i18n/navigation";
import {
  displayName,
  handoffPreviewText,
  normalizeEmail,
  normalizePhone,
} from "@/lib/inquiry-handoff";
import { shouldShowFirstWebsiteInquiryMarker } from "@/lib/first-website-inquiry";
import type { Lead, LeadStatus } from "@/lib/types";

interface InquiryCardProps {
  lead: Lead;
  createdLabel: string;
  statusUpdating: boolean;
  onStatusChange: (status: LeadStatus) => void;
}

export function InquiryCard({
  lead,
  createdLabel,
  statusUpdating,
  onStatusChange,
}: InquiryCardProps) {
  const t = useTranslations("leads");
  const phone = normalizePhone(lead);
  const email = normalizeEmail(lead);
  const urgency = lead.urgency?.trim() || null;
  const preview = handoffPreviewText(lead, t("noDescription"));
  const showFirstWebsiteMarker = shouldShowFirstWebsiteInquiryMarker(lead);

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
          <InquirySourceBadge source={lead.source} />
          <StatusBadge status={lead.status} />
          <time className="inquiry-card-date muted" dateTime={lead.created_at}>
            {createdLabel}
          </time>
        </div>
      </div>

      {urgency ? (
        <p className="inquiry-card-urgency">
          <span className="inquiry-card-urgency-label">{t("urgency")}</span>
          <span className="inquiry-card-urgency-value">{urgency}</span>
        </p>
      ) : null}

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

      <div className="inquiry-card-actions">
        {phone ? (
          <a href={`tel:${phone}`} className="button secondary">
            {t("call")}
          </a>
        ) : null}
        {email ? (
          <a href={`mailto:${email}`} className="button secondary">
            {t("emailAction")}
          </a>
        ) : null}
        <Link href={`/leads/${lead.id}`} className="button secondary">
          {t("openDetails")}
        </Link>
      </div>

      <div className="inquiry-card-status">
        <span className="inquiry-card-status-label">{t("status")}</span>
        <StatusSelect
          value={lead.status}
          disabled={statusUpdating}
          onChange={onStatusChange}
        />
      </div>
    </article>
  );
}
