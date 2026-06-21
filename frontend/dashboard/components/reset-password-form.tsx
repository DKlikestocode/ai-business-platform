"use client";

import { FormEvent, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";

import { LegalFooterLinks } from "@/components/legal-footer-links";
import { AlertBanner } from "@/components/ui/alert-banner";
import { resetPassword } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import { Link } from "@/i18n/navigation";

export function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token")?.trim() ?? "";
  const t = useTranslations("resetPassword");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setError(t("missingToken"));
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await resetPassword({ token, password });
      setSuccess(true);
    } catch (err) {
      setError(formatUserFacingError(err, t("failed"), errorMessages));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-layout">
        <div className="login-card card">
          <h1>{t("title")}</h1>
          <p className="muted">{t("description")}</p>

          {!token ? <AlertBanner>{t("missingToken")}</AlertBanner> : null}
          {success ? <AlertBanner variant="success">{t("success")}</AlertBanner> : null}
          {error ? <AlertBanner>{error}</AlertBanner> : null}

          <form className="login-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>{t("passwordLabel")}</span>
              <input
                className="input"
                type="password"
                autoComplete="new-password"
                minLength={8}
                required
                value={password}
                disabled={submitting || success || !token}
                onChange={(event) => setPassword(event.target.value)}
              />
              <p className="muted field-hint">{t("passwordHint")}</p>
            </label>

            <button
              type="submit"
              className="button"
              disabled={submitting || success || !token || password.length < 8}
            >
              {submitting ? t("submitting") : t("submit")}
            </button>
          </form>

          <p className="muted onboarding-footer">
            <Link href="/login">{t("backToLogin")}</Link>
          </p>
        </div>
        <LegalFooterLinks />
      </div>
    </div>
  );
}
