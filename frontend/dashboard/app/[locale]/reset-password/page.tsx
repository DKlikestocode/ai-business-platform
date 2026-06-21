import { Suspense } from "react";
import { getTranslations } from "next-intl/server";

import { ResetPasswordForm } from "@/components/reset-password-form";

export default async function ResetPasswordPage() {
  const t = await getTranslations("login");

  return (
    <Suspense fallback={<div className="login-page muted">{t("loading")}</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
