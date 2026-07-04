"use client";

import type { ReactNode } from "react";
import { useTranslations } from "next-intl";

import { LegalFooterLinks } from "@/components/legal-footer-links";
import { LocaleSwitcher } from "@/components/locale-switcher";
import { PilotBookingLink } from "@/components/pilot-booking-link";
import { Link } from "@/i18n/navigation";

interface MarketingShellClientProps {
  children: ReactNode;
}

export function MarketingShellClient({ children }: MarketingShellClientProps) {
  const brand = useTranslations("brand");
  const nav = useTranslations("nav");
  const legal = useTranslations("legal");

  return (
    <div className="marketing-page">
      <header className="marketing-header shell">
        <Link href="/" className="brand-link marketing-header-brand">
          <span className="brand-mark">{brand("mark")}</span>
          <span>{brand("name")}</span>
        </Link>
        <nav className="marketing-nav" aria-label={nav("marketing")}>
          <Link href="/login" className="nav-link">
            {nav("signIn")}
          </Link>
          <PilotBookingLink className="button marketing-nav-cta">
            {nav("bookPilot")}
          </PilotBookingLink>
          <LocaleSwitcher />
        </nav>
      </header>
      <main>{children}</main>
      <footer className="marketing-footer shell">
        <div className="marketing-footer-brand">
          <Link href="/" className="brand-link brand-link-footer">
            <span className="brand-mark">{brand("mark")}</span>
            <span>{brand("name")}</span>
          </Link>
          <p className="muted marketing-footer-tagline">{brand("tagline")}</p>
        </div>
        <nav className="legal-footer-links" aria-label={legal("footerNav")}>
          <Link href="/impressum">{legal("impressumLink")}</Link>
          <Link href="/datenschutz">{legal("datenschutzLink")}</Link>
        </nav>
      </footer>
    </div>
  );
}
