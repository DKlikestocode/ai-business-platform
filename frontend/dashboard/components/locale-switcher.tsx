"use client";

import { useLocale, useTranslations } from "next-intl";

import { usePathname, useRouter } from "@/i18n/navigation";
import { routing, type AppLocale } from "@/i18n/routing";

const LOCALE_OPTION_KEYS = {
  de: "localeNameDe",
  en: "localeNameEn",
} as const satisfies Record<AppLocale, "localeNameDe" | "localeNameEn">;

export function LocaleSwitcher() {
  const locale = useLocale() as AppLocale;
  const pathname = usePathname();
  const router = useRouter();
  const t = useTranslations("common");

  function switchLocale(nextLocale: AppLocale) {
    if (nextLocale === locale) {
      return;
    }

    router.replace(pathname, { locale: nextLocale });
  }

  return (
    <div className="locale-switcher-anchor">
      <label className="sr-only" htmlFor="locale-switcher-select">
        {t("language")}
      </label>
      <select
        id="locale-switcher-select"
        className="select locale-switcher-select"
        value={locale}
        aria-label={t("language")}
        onChange={(event) => switchLocale(event.target.value as AppLocale)}
      >
        {routing.locales.map((code) => (
          <option key={code} value={code}>
            {t(LOCALE_OPTION_KEYS[code])}
          </option>
        ))}
      </select>
    </div>
  );
}
