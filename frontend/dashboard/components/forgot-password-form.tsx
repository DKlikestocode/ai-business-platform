"use client";

import { FormEvent, useState } from "react";
import { useTranslations } from "next-intl";

import { LegalFooterLinks } from "@/components/legal-footer-links";
import { AlertBanner } from "@/components/ui/alert-banner";
import { requestPasswordReset } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import { Link } from "@/i18n/navigation";

export function ForgotPasswordForm() {
  const t = useTranslations("forgotPassword");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(false);

    try {
      await requestPasswordReset({ email: email.trim() });
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

          {success ? (
            <AlertBanner variant="success">{t("success")}</AlertBanner>
          ) : null}
          {error ? <AlertBanner>{error}</AlertBanner> : null}

          <form className="login-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>{t("emailLabel")}</span>
              <input
                className="input"
                type="email"
                autoComplete="email"
                required
                value={email}
                disabled={submitting || success}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>

            <button
              type="submit"
              className="button"
              disabled={submitting || success || !email.trim()}
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
