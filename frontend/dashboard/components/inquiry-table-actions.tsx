"use client";

import { useTranslations } from "next-intl";

import { shouldShowMarkContactedAction } from "@/lib/inquiry-callback-loop";
import { normalizeEmail, normalizePhone } from "@/lib/inquiry-handoff";
import type { Lead } from "@/lib/types";

interface InquiryTableActionsProps {
  lead: Lead;
  updating: boolean;
  onMarkContacted: () => void;
}

export function InquiryTableActions({
  lead,
  updating,
  onMarkContacted,
}: InquiryTableActionsProps) {
  const t = useTranslations("leads");
  const tDetail = useTranslations("leadDetail");
  const phone = normalizePhone(lead);
  const email = normalizeEmail(lead);
  const hasContact = Boolean(phone || email);
  const showMarkContacted = shouldShowMarkContactedAction(hasContact, lead.status);

  return (
    <div className="inquiry-table-actions">
      {phone ? (
        <a href={`tel:${phone}`} className="button secondary inquiry-table-action">
          {t("call")}
        </a>
      ) : null}
      {email ? (
        <a href={`mailto:${email}`} className="button secondary inquiry-table-action">
          {t("emailAction")}
        </a>
      ) : null}
      {showMarkContacted ? (
        <button
          type="button"
          className="button secondary inquiry-table-action"
          disabled={updating}
          onClick={onMarkContacted}
        >
          {tDetail("markContacted")}
        </button>
      ) : null}
    </div>
  );
}
