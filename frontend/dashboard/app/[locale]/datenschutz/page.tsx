import { getTranslations, setRequestLocale } from "next-intl/server";

import { MarketingShell } from "@/components/marketing-shell";
import { routing, type AppLocale } from "@/i18n/routing";

type DatenschutzPageProps = {
  params: Promise<{ locale: string }>;
};

const SECTION_KEYS = [
  "controller",
  "dataCollected",
  "purpose",
  "legalBasis",
  "hosting",
  "processors",
  "retention",
  "rights",
  "security",
  "changes",
] as const;

export default async function DatenschutzPage({ params }: DatenschutzPageProps) {
  const { locale } = await params;
  setRequestLocale(locale as AppLocale);
  const t = await getTranslations("legal.datenschutz");

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
