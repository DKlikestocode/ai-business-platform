"use client";

import { useLocale, useTranslations } from "next-intl";

import { usePathname, useRouter } from "@/i18n/navigation";
import { routing, type AppLocale } from "@/i18n/routing";

const LOCALE_LABEL_KEYS = {
  de: "localeDe",
  en: "localeEn",
} as const satisfies Record<AppLocale, "localeDe" | "localeEn">;

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
    <div className="locale-switcher" role="group" aria-label={t("language")}>
      {routing.locales.map((code) => (
        <button
          key={code}
          type="button"
          className={`locale-switcher-option${
            code === locale ? " is-active" : ""
          }`}
          aria-pressed={code === locale}
          onClick={() => switchLocale(code)}
        >
          {t(LOCALE_LABEL_KEYS[code])}
        </button>
      ))}
    </div>
  );
}
