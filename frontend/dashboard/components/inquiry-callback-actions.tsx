"use client";

import { useTranslations } from "next-intl";

import {
  getPrimaryContactAction,
  shouldShowMarkContactedAction,
} from "@/lib/inquiry-callback-loop";
import type { LeadStatus } from "@/lib/types";

interface InquiryCallbackActionsProps {
  phone: string | null;
  email: string | null;
  status: LeadStatus;
  hasContact: boolean;
  updating: boolean;
  showContactedSuccess: boolean;
  onMarkContacted: () => void;
}

export function InquiryCallbackActions({
  phone,
  email,
  status,
  hasContact,
  updating,
  showContactedSuccess,
  onMarkContacted,
}: InquiryCallbackActionsProps) {
  const t = useTranslations("leadDetail");
  const primaryAction = getPrimaryContactAction(phone, email);
  const showMarkContacted = shouldShowMarkContactedAction(hasContact, status);

  if (!hasContact) {
    return (
      <div className="inquiry-handoff-actions inquiry-callback-actions">
        <p className="inquiry-handoff-missing-contact">{t("missingContact")}</p>
      </div>
    );
  }

  return (
    <div className="inquiry-callback-actions">
      <div className="inquiry-handoff-actions">
        {phone ? (
          <a
            href={`tel:${phone}`}
            className="button inquiry-handoff-call"
            aria-label={`${t("call")} ${phone}`}
          >
            {t("call")}
          </a>
        ) : null}
        {email ? (
          <a
            href={`mailto:${email}`}
            className={
              primaryAction === "email"
                ? "button inquiry-handoff-call"
                : "button secondary inquiry-handoff-email"
            }
            aria-label={`${t("emailAction")} ${email}`}
          >
            {t("emailAction")}
          </a>
        ) : null}
      </div>

      {showMarkContacted ? (
        <div className="inquiry-callback-followup">
          <p className="inquiry-callback-hint muted">{t("markContactedHint")}</p>
          <button
            type="button"
            className="button secondary inquiry-callback-mark"
            disabled={updating}
            onClick={onMarkContacted}
          >
            {t("markContacted")}
          </button>
        </div>
      ) : null}

      {showContactedSuccess ? (
        <p className="inquiry-callback-success" role="status" aria-live="polite">
          {t("markContactedSuccess")}
        </p>
      ) : null}
    </div>
  );
}
