"use client";

import { useTranslations } from "next-intl";

import { StatusBadge } from "@/components/status-badge";
import { InquirySourceBadge } from "@/components/inquiry-source-badge";
import { StatusSelect } from "@/components/status-select";
import { Link } from "@/i18n/navigation";
import type { Lead, LeadStatus } from "@/lib/types";

interface InquiryCardProps {
  lead: Lead;
  createdLabel: string;
  statusUpdating: boolean;
  onStatusChange: (status: LeadStatus) => void;
}

function hasPhone(value: string | null | undefined): value is string {
  return Boolean(value?.trim());
}

function hasEmail(value: string | null | undefined): value is string {
  return Boolean(value?.trim());
}

function previewText(lead: Lead, noDescriptionLabel: string): string {
  const summary = lead.summary?.trim();
  if (summary) {
    return summary;
  }

  const description = lead.description?.trim();
  if (description) {
    return description;
  }

  const service = lead.service_requested?.trim();
  if (service) {
    return service;
  }

  return noDescriptionLabel;
}

export function InquiryCard({
  lead,
  createdLabel,
  statusUpdating,
  onStatusChange,
}: InquiryCardProps) {
  const t = useTranslations("leads");
  const phone = hasPhone(lead.phone) ? lead.phone.trim() : null;
  const email = hasEmail(lead.email) ? lead.email.trim() : null;
  const urgency = lead.urgency?.trim() || null;
  const preview = previewText(lead, t("noDescription"));

  return (
    <article className="inquiry-card card">
      <div className="inquiry-card-header">
        <div className="inquiry-card-intro">
          <h3 className="inquiry-card-name">
            <Link href={`/leads/${lead.id}`} className="link">
              {lead.name}
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
