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

  return (
    <div className="marketing-page">
      <header className="marketing-header shell">
        <Link href="/" className="brand-link">
          <span className="brand-mark">{brand("mark")}</span>
          <span>{brand("name")}</span>
        </Link>
        <nav className="marketing-nav" aria-label={nav("marketing")}>
          <LocaleSwitcher />
          <Link href="/login" className="nav-link">
            {nav("signIn")}
          </Link>
          <PilotBookingLink className="button">
            {nav("bookPilot")}
          </PilotBookingLink>
        </nav>
      </header>
      <main>{children}</main>
      <footer className="marketing-footer shell">
        <p className="muted">{brand("tagline")}</p>
        <LegalFooterLinks />
      </footer>
    </div>
  );
}
