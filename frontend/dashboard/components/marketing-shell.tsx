import { getTranslations } from "next-intl/server";
import type { ReactNode } from "react";

import { Link } from "@/i18n/navigation";

interface MarketingShellProps {
  children: ReactNode;
}

export async function MarketingShell({ children }: MarketingShellProps) {
  const brand = await getTranslations("brand");
  const nav = await getTranslations("nav");
  const legal = await getTranslations("legal");

  return (
    <div className="marketing-page">
      <header className="marketing-header shell">
        <Link href="/" className="brand-link">
          <span className="brand-mark">{brand("mark")}</span>
          <span>{brand("name")}</span>
        </Link>
        <nav className="marketing-nav" aria-label={nav("marketing")}>
          <Link href="/login" className="nav-link">
            {nav("signIn")}
          </Link>
          <Link href="/onboarding" className="button">
            {nav("startFreePilot")}
          </Link>
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
