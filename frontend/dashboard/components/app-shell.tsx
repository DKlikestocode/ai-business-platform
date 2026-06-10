"use client";

import type { ReactNode } from "react";

import { CompanyLabel } from "@/components/auth-provider";
import { SiteNav } from "@/components/site-nav";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <header className="header">
        <div className="header-top">
          <div>
            <h1>AI Agent Platform</h1>
            <p className="muted">Lead capture, qualification, and team dashboard</p>
            <CompanyLabel />
          </div>
          <SiteNav />
        </div>
      </header>
      {children}
    </div>
  );
}
