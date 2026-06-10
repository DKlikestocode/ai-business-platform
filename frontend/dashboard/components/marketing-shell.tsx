import Link from "next/link";
import type { ReactNode } from "react";

interface MarketingShellProps {
  children: ReactNode;
}

export function MarketingShell({ children }: MarketingShellProps) {
  return (
    <div className="marketing-page">
      <header className="marketing-header shell">
        <Link href="/" className="brand-link">
          <span className="brand-mark">AI</span>
          <span>Agent Platform</span>
        </Link>
        <nav className="marketing-nav" aria-label="Marketing navigation">
          <Link href="/login" className="nav-link">
            Sign in
          </Link>
          <Link href="/onboarding" className="button">
            Start free pilot
          </Link>
        </nav>
      </header>
      <main>{children}</main>
      <footer className="marketing-footer shell">
        <p className="muted">
          Lead capture, qualification, and notifications for service businesses.
        </p>
      </footer>
    </div>
  );
}
