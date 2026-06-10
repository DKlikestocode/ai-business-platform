import { setRequestLocale } from "next-intl/server";

import { LandingPage } from "@/components/landing-page";
import { routing, type AppLocale } from "@/i18n/routing";

type HomePageProps = {
  params: Promise<{ locale: string }>;
};

export default async function HomePage({ params }: HomePageProps) {
  const { locale } = await params;
  setRequestLocale(locale as AppLocale);

  return <LandingPage />;
}
