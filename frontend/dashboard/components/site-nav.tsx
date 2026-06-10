"use client";

import { useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { Link } from "@/i18n/navigation";
import { isDevelopment } from "@/lib/env";

const links = [
  { href: "/getting-started", labelKey: "gettingStarted" },
  { href: "/leads", labelKey: "leads" },
  { href: "/demo-chat", labelKey: "demoChat" },
  { href: "/settings", labelKey: "settings" },
] as const;

export function SiteNav() {
  const { logout, user } = useAuth();
  const t = useTranslations("nav");
  const tCommon = useTranslations("common");

  return (
    <nav className="site-nav" aria-label={t("main")}>
      {links.map((link) => (
        <Link key={link.href} href={link.href} className="nav-link">
          {t(link.labelKey)}
        </Link>
      ))}
      {isDevelopment ? (
        <span className="nav-badge" title={tCommon("devMode")}>
          {tCommon("dev")}
        </span>
      ) : null}
      {user ? (
        <button
          type="button"
          className="button secondary nav-button"
          onClick={() => void logout()}
        >
          {t("signOut")}
        </button>
      ) : null}
    </nav>
  );
}
