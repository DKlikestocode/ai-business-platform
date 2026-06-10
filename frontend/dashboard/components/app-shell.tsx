"use client";

import type { ReactNode } from "react";
import { useTranslations } from "next-intl";

import { CompanyLabel } from "@/components/auth-provider";
import { SiteNav } from "@/components/site-nav";

export function AppShell({ children }: { children: ReactNode }) {
  const t = useTranslations("appShell");

  return (
    <div className="shell">
      <header className="header">
        <div className="header-top">
          <div>
            <h1>{t("title")}</h1>
            <p className="muted">{t("subtitle")}</p>
            <CompanyLabel />
          </div>
          <SiteNav />
        </div>
      </header>
      {children}
    </div>
  );
}
