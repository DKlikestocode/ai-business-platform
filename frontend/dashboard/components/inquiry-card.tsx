"use client";

import { useTranslations } from "next-intl";

import { FirstWebsiteInquiryMarker } from "@/components/first-website-inquiry-marker";
import { InquiryCallbackActions } from "@/components/inquiry-callback-actions";
import { InquiryContactedIndicator } from "@/components/inquiry-contacted-indicator";
import { InquiryCustomerConfirmationIndicator } from "@/components/inquiry-customer-confirmation-indicator";
import { InquiryNotificationIndicator } from "@/components/inquiry-notification-indicator";
import { Link } from "@/i18n/navigation";
import {
  displayName,
  handoffPreviewText,
  normalizeEmail,
  normalizePhone,
} from "@/lib/inquiry-handoff";
import { isAppointmentConfirmationSent } from "@/lib/appointment-confirmation";
import { shouldShowFirstWebsiteInquiryMarker } from "@/lib/first-website-inquiry";
import { shouldShowCustomerConfirmationIndicator } from "@/lib/inquiry-customer-confirmation";
import type { Lead } from "@/lib/types";

interface InquiryCardProps {
  lead: Lead;
  createdLabel: string;
  statusUpdating: boolean;
  showContactedSuccess: boolean;
  sendCustomerConfirmation?: boolean;
  contactedMode?: boolean;
  onMarkContacted: () => void;
  onRestore?: () => void;
  onDelete?: () => void;
}

export function InquiryCard({
  lead,
  createdLabel: _createdLabel,
  statusUpdating,
  showContactedSuccess,
  sendCustomerConfirmation = false,
  contactedMode = false,
  onMarkContacted,
  onRestore,
  onDelete,
}: InquiryCardProps) {
  const t = useTranslations("leads");
  const phone = normalizePhone(lead);
  const email = normalizeEmail(lead);
  const preview = handoffPreviewText(lead, t("noDescription"));
  const showFirstWebsiteMarker = shouldShowFirstWebsiteInquiryMarker(lead);
  const showCustomerConfirmation = shouldShowCustomerConfirmationIndicator(
    sendCustomerConfirmation,
    lead.customer_confirmation_sent_at,
  );
  const showAppointmentConfirmationSent = isAppointmentConfirmationSent(
    lead.appointment_confirmation_sent_at,
  );

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
      </div>

      <InquiryNotificationIndicator
        notificationSentAt={lead.notification_sent_at}
      />

      {showCustomerConfirmation ? (
        <InquiryCustomerConfirmationIndicator
          customerConfirmationSentAt={lead.customer_confirmation_sent_at}
        />
      ) : null}

      {showAppointmentConfirmationSent ? (
        <p className="inquiry-card-appointment-sent muted">
          {t("appointmentConfirmationSent")}
        </p>
      ) : null}

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
