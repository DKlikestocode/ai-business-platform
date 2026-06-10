import { CompanySettingsForm } from "@/components/company-settings-form";
import { PageHeader } from "@/components/ui/page-header";

export default function SettingsPage() {
  return (
    <div className="stack">
      <PageHeader
        title="Settings"
        description="Manage company profile, lead notifications, and website widget embed."
      />
      <CompanySettingsForm />
    </div>
  );
}
