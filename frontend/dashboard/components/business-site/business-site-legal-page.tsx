import Link from "next/link";

import { getBusinessSiteCopy } from "@/lib/business-site-copy";
import {
  getBusinessSiteLegalCopy,
  type BusinessSiteLegalVariant,
} from "@/lib/business-site-legal-copy";
import type { PublicBusinessSite } from "@/lib/business-site";
import { getBusinessSitePublicBasePath } from "@/lib/site-config";

interface BusinessSiteLegalPageProps {
  site: PublicBusinessSite;
  variant: BusinessSiteLegalVariant;
}

export function BusinessSiteLegalPage({
  site,
  variant,
}: BusinessSiteLegalPageProps) {
  const copy = getBusinessSiteCopy("de");
  const legal = getBusinessSiteLegalCopy("de", variant, site);
  const basePath = getBusinessSitePublicBasePath();

  return (
    <div className="business-site">
      <header className="business-site-header">
        <div className="business-site-container business-site-header-inner">
          <div className="business-site-brand">
            <strong>{site.company_name}</strong>
          </div>
          <Link className="button secondary business-site-cta-secondary" href={basePath || "/"}>
            {copy.legalBackHome}
          </Link>
        </div>
      </header>

      <main>
        <article className="business-site-container business-site-legal-page">
          <h1>{legal.title}</h1>
          <p className="muted business-site-legal-intro">{legal.intro}</p>
          {legal.sections.map((section) => (
            <section key={section.heading} className="business-site-legal-section">
              <h2>{section.heading}</h2>
              <p>{section.body}</p>
            </section>
          ))}
        </article>
      </main>

      <footer className="business-site-footer">
        <div className="business-site-container business-site-footer-inner">
          <div>
            <strong>{site.company_name}</strong>
          </div>
          <nav className="business-site-footer-legal" aria-label={copy.legalNavLabel}>
            <Link href={`${basePath}/impressum`}>{copy.impressumLink}</Link>
            <Link href={`${basePath}/datenschutz`}>{copy.datenschutzLink}</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
