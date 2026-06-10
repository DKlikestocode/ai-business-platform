import { Suspense } from "react";
import { getTranslations } from "next-intl/server";

import { LoginForm } from "@/components/login-form";

export default async function LoginPage() {
  const t = await getTranslations("login");

  return (
    <Suspense fallback={<div className="login-page muted">{t("loading")}</div>}>
      <LoginForm />
    </Suspense>
  );
}
