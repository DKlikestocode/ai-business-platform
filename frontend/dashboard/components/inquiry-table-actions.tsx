"use client";

import { useTranslations } from "next-intl";

import { shouldShowMarkContactedAction } from "@/lib/inquiry-callback-loop";
import { normalizeEmail, normalizePhone } from "@/lib/inquiry-handoff";
import type { Lead } from "@/lib/types";

interface InquiryTableActionsProps {
  lead: Lead;
  updating: boolean;
  contactedMode?: boolean;
  onMarkContacted: () => void;
  onRestore?: () => void;
}

export function InquiryTableActions({
  lead,
  updating,
  contactedMode = false,
  onMarkContacted,
  onRestore,
}: InquiryTableActionsProps) {
  const t = useTranslations("leads");
  const tDetail = useTranslations("leadDetail");
  const phone = normalizePhone(lead);
  const email = normalizeEmail(lead);
  const showMarkContacted =
    !contactedMode && shouldShowMarkContactedAction(lead.status);

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
      {contactedMode && onRestore ? (
        <button
          type="button"
          className="button inquiry-table-action"
          disabled={updating}
          onClick={onRestore}
        >
          {t("restore")}
        </button>
      ) : null}
    </div>
  );
}
