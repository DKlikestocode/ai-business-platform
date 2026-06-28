"use client";

import { getBusinessSiteCopy } from "@/lib/business-site-copy";

export default function SiteErrorPage() {
  const copy = getBusinessSiteCopy("de");

  return (
    <div className="business-site">
      <main className="business-site-container business-site-error">
        <h1>{copy.loadFailedTitle}</h1>
        <p className="muted">{copy.loadFailedBody}</p>
      </main>
    </div>
  );
}
