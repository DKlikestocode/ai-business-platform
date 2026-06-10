type AlertVariant = "error" | "success" | "info";

import type { ReactNode } from "react";

interface AlertBannerProps {
  variant?: AlertVariant;
  children: ReactNode;
}

const CLASS_BY_VARIANT: Record<AlertVariant, string> = {
  error: "alert",
  success: "notice",
  info: "info-banner",
};

export function AlertBanner({
  variant = "error",
  children,
}: AlertBannerProps) {
  return <div className={CLASS_BY_VARIANT[variant]}>{children}</div>;
}
