"use client";

import { useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";
import { useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import { Link, useRouter } from "@/i18n/navigation";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, loading, error } = useAuth();
  const t = useTranslations("login");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setSubmitting(true);

    try {
      await login(email.trim(), password);
      const nextPath = searchParams.get("next");
      router.replace(
        nextPath && nextPath.startsWith("/") ? nextPath : "/getting-started",
      );
    } catch (err) {
      setFormError(
        formatUserFacingError(err, t("signInFailed"), errorMessages),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card card">
        <h1>{t("title")}</h1>
        <p className="muted">{t("description")}</p>
        <p className="muted onboarding-footer">
          {t("newCustomer")} <Link href="/onboarding">{t("startPilot")}</Link>
        </p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>{tCommon("email")}</span>
            <input
              className="input"
              type="email"
              autoComplete="email"
              required
              value={email}
              disabled={loading || submitting}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>

          <label className="field">
            <span>{tCommon("password")}</span>
            <input
              className="input"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              disabled={loading || submitting}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>

          {formError || error ? (
            <AlertBanner>{formError ?? error}</AlertBanner>
          ) : null}

          <button
            type="submit"
            className="button"
            disabled={loading || submitting || !email || !password}
          >
            {submitting ? t("signingIn") : t("signIn")}
          </button>
        </form>
      </div>
    </div>
  );
}
