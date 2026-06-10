import { getTranslations, setRequestLocale } from "next-intl/server";

import { MarketingShell } from "@/components/marketing-shell";
import { routing, type AppLocale } from "@/i18n/routing";

type ImpressumPageProps = {
  params: Promise<{ locale: string }>;
};

const SECTION_KEYS = [
  "operator",
  "contact",
  "register",
  "vat",
  "responsible",
  "dispute",
] as const;

export default async function ImpressumPage({ params }: ImpressumPageProps) {
  const { locale } = await params;
  setRequestLocale(locale as AppLocale);
  const t = await getTranslations("legal.impressum");

  return (
    <MarketingShell>
      <article className="legal-page shell">
        <h1>{t("title")}</h1>
        <p className="muted legal-intro">{t("intro")}</p>
        {SECTION_KEYS.map((key) => (
          <section key={key} className="legal-section">
            <h2>{t(`${key}Heading`)}</h2>
            <p>{t(`${key}Body`)}</p>
          </section>
        ))}
      </article>
    </MarketingShell>
  );
}

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}
