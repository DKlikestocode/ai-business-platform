import { getTranslations } from "next-intl/server";

import { CompanySettingsForm } from "@/components/company-settings-form";
import { PageHeader } from "@/components/ui/page-header";

export default async function SettingsPage() {
  const t = await getTranslations("settings");

  return (
    <div className="stack">
      <PageHeader title={t("pageTitle")} description={t("pageDescription")} />
      <CompanySettingsForm />
    </div>
  );
}
