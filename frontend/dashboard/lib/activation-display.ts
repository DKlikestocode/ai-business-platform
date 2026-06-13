import type { ActivationStatus } from "@/lib/types";

export function isActivationSetupLive(
  status: ActivationStatus | null | undefined,
): boolean {
  return status === "live";
}

export function formatActivationTimestamp(
  value: string | null,
  locale: string,
): string | null {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return new Intl.DateTimeFormat(locale, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function activationStatusClassName(status: ActivationStatus): string {
  return `activation-status activation-status--${status}`;
}

export function embedSnippetIncludesInstallToken(snippet: string): boolean {
  return snippet.includes("data-install-token=");
}
