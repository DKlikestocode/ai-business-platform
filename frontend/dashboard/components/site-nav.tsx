"use client";

import { useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { LocaleSwitcher } from "@/components/locale-switcher";
import { Link } from "@/i18n/navigation";
import { isDevelopment } from "@/lib/env";
import { useGettingStartedNavVisibility } from "@/lib/use-getting-started-nav-visibility";

const links = [
  { href: "/getting-started", labelKey: "gettingStarted", setupOnly: true as const },
  { href: "/leads", labelKey: "leads", setupOnly: false as const },
  { href: "/demo-chat", labelKey: "demoChat", setupOnly: false as const },
  { href: "/settings", labelKey: "settings", setupOnly: false as const },
] as const;

export function SiteNav() {
  const { logout, user } = useAuth();
  const { showGettingStarted } = useGettingStartedNavVisibility();
  const t = useTranslations("nav");
  const tCommon = useTranslations("common");

  const visibleLinks = links.filter(
    (link) => !link.setupOnly || showGettingStarted,
  );

  return (
    <nav className="site-nav" aria-label={t("main")}>
      <LocaleSwitcher />
      {visibleLinks.map((link) => (
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
