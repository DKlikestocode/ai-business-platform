import type { useTranslations } from "next-intl";

export type ErrorTranslator = ReturnType<typeof useTranslations<"errors">>;

export function getErrorMessages(t: ErrorTranslator) {
  return {
    openai: t("openai"),
    session: t("sessionExpired"),
    network: t("network"),
    duplicateEmail: t("duplicateEmail"),
  };
}
