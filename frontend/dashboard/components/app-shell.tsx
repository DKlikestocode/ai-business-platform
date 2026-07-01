"use client";

import type { ReactNode } from "react";
import { useTranslations } from "next-intl";

import { CompanyLabel } from "@/components/auth-provider";
import { GettingStartedLauncher } from "@/components/getting-started-launcher";
import { LegalFooterLinks } from "@/components/legal-footer-links";
import { SiteNav } from "@/components/site-nav";
import { Link } from "@/i18n/navigation";

export function AppShell({ children }: { children: ReactNode }) {
  const t = useTranslations("appShell");
  const brand = useTranslations("brand");

  return (
    <div className="app-page">
      <header className="app-header">
        <div className="shell app-header-inner">
          <div className="app-header-brand">
            <Link href="/leads" className="brand-link app-brand-link">
              <span className="brand-mark">{brand("mark")}</span>
              <span className="app-brand-text">
                <span className="app-brand-name">{t("title")}</span>
                <span className="app-brand-subtitle muted">{t("subtitle")}</span>
              </span>
            </Link>
            <CompanyLabel />
          </div>
          <SiteNav />
        </div>
      </header>
      <main className="shell app-main">{children}</main>
      <footer className="shell app-footer">
        <LegalFooterLinks />
      </footer>
      <GettingStartedLauncher />
    </div>
  );
}
