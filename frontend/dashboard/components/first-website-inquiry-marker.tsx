"use client";

import { useTranslations } from "next-intl";

interface FirstWebsiteInquiryMarkerProps {
  variant?: "card" | "detail";
}

export function FirstWebsiteInquiryMarker({
  variant = "card",
}: FirstWebsiteInquiryMarkerProps) {
  const t = useTranslations(
    variant === "detail" ? "leadDetail" : "leads",
  );

  return (
    <div
      className="first-website-inquiry-marker"
      role="status"
      aria-live="polite"
    >
      <p className="first-website-inquiry-marker-title">
        {t("firstWebsiteInquiryTitle")}
      </p>
      <p className="first-website-inquiry-marker-body muted">
        {t("firstWebsiteInquiryBody")}
      </p>
    </div>
  );
}
