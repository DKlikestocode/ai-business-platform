"use client";

import { useTranslations } from "next-intl";

import { Link } from "@/i18n/navigation";

export function LegalFooterLinks() {
  const t = useTranslations("legal");

  return (
    <nav className="legal-footer-links" aria-label={t("footerNav")}>
      <Link href="/impressum">{t("impressumLink")}</Link>
      <Link href="/datenschutz">{t("datenschutzLink")}</Link>
    </nav>
  );
}
