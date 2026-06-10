"use client";

import Link from "next/link";

import { useAuth } from "@/components/auth-provider";
import { isDevelopment } from "@/lib/env";

const links = [
  { href: "/getting-started", label: "Getting Started" },
  { href: "/leads", label: "Leads" },
  { href: "/demo-chat", label: "Demo Chat" },
  { href: "/settings", label: "Settings" },
];

export function SiteNav() {
  const { logout, user } = useAuth();

  return (
    <nav className="site-nav" aria-label="Main navigation">
      {links.map((link) => (
        <Link key={link.href} href={link.href} className="nav-link">
          {link.label}
        </Link>
      ))}
      {isDevelopment ? (
        <span className="nav-badge" title="Development mode">
          Dev
        </span>
      ) : null}
      {user ? (
        <button type="button" className="button secondary nav-button" onClick={() => void logout()}>
          Sign out
        </button>
      ) : null}
    </nav>
  );
}
