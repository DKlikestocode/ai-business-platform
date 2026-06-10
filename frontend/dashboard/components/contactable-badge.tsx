"use client";

import { useTranslations } from "next-intl";

import { contactableBadgeClass } from "@/lib/lead-qualification";

interface ContactableBadgeProps {
  contactable: boolean;
}

export function ContactableBadge({ contactable }: ContactableBadgeProps) {
  const t = useTranslations("common");

  return (
    <span className={`badge ${contactableBadgeClass(contactable)}`}>
      {contactable ? t("yes") : t("no")}
    </span>
  );
}
