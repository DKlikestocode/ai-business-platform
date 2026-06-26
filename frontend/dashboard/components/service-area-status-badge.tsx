"use client";

import { useTranslations } from "next-intl";

import type { ServiceAreaStatus } from "@/lib/types";

interface ServiceAreaStatusBadgeProps {
  status: ServiceAreaStatus | null | undefined;
  distanceKm?: number | null;
}

export function ServiceAreaStatusBadge({
  status,
  distanceKm,
}: ServiceAreaStatusBadgeProps) {
  const t = useTranslations("leads");

  if (!status || status === "not_configured" || status === "unknown") {
    return null;
  }

  const label =
    status === "in_range"
      ? t("serviceAreaInRange")
      : t("serviceAreaOutOfRange");

  const distance =
    distanceKm != null && Number.isFinite(distanceKm)
      ? t("serviceAreaDistance", { km: Math.round(distanceKm) })
      : null;

  return (
    <span
      className={`badge service-area-badge service-area-badge--${status}`}
      title={distance ?? undefined}
    >
      {label}
      {distance ? ` · ${distance}` : null}
    </span>
  );
}
