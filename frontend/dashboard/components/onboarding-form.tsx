"use client";

import { FormEvent, useState } from "react";
import { useTranslations } from "next-intl";

import { MarketingShellClient } from "@/components/marketing-shell-client";
import { AlertBanner } from "@/components/ui/alert-banner";
import { useAuth } from "@/components/auth-provider";
import { registerCompany, registerUser } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";
import { getErrorMessages } from "@/lib/i18n-error-messages";
import { Link, useRouter } from "@/i18n/navigation";

type Step = "company" | "user";

export function OnboardingForm() {
  const router = useRouter();
  const { login } = useAuth();
  const t = useTranslations("onboarding");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const errorMessages = getErrorMessages(tErrors);
  const [step, setStep] = useState<Step>("company");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);

  const [companyName, setCompanyName] = useState("");
  const [companyEmail, setCompanyEmail] = useState("");
  const [companyPhone, setCompanyPhone] = useState("");
  const [companyId, setCompanyId] = useState<string | null>(null);

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleCompanySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const company = await registerCompany({
        name: companyName.trim(),
        email: companyEmail.trim(),
        phone: companyPhone.trim() || undefined,
      });
      setCompanyId(company.id);
      setStep("user");
    } catch (err) {
      setError(formatUserFacingError(err, t("createCompanyFailed"), errorMessages));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleUserSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!companyId) {
      setError(t("createCompanyFirst"));
      return;
    }

    if (!privacyAccepted) {
      setError(t("privacyConsentRequired"));
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await registerUser({
        company_id: companyId,
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: userEmail.trim(),
        password,
        role: "owner",
      });
      await login(userEmail.trim(), password);
      router.replace("/leads");
    } catch (err) {
      setError(formatUserFacingError(err, t("createUserFailed"), errorMessages));
    } finally {
      setSubmitting(false);
    }
  }

  const stepLabel = step === "company" ? t("stepCompany") : t("stepUser");

  return (
    <MarketingShellClient>
      <section className="onboarding-section shell">
        <div className="onboarding-card card">
          <p className="eyebrow">{t("eyebrow")}</p>
          <h1>{t("title")}</h1>
          <p className="muted">{t("subtitle")}</p>
          <p className="muted">
            {t("stepOf", {
              step: step === "company" ? "1" : "2",
              label: stepLabel,
            })}
          </p>

          <div className="step-indicator" aria-hidden="true">
            <span className={step === "company" ? "step active" : "step done"} />
            <span className={step === "user" ? "step active" : "step"} />
          </div>

          {error ? <AlertBanner>{error}</AlertBanner> : null}

          {step === "company" ? (
            <form className="onboarding-form" onSubmit={handleCompanySubmit}>
              <label className="field">
                <span>{t("companyName")}</span>
                <input
                  className="input"
                  value={companyName}
                  onChange={(event) => setCompanyName(event.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
              <label className="field">
                <span>{t("companyEmail")}</span>
                <input
                  className="input"
                  type="email"
                  value={companyEmail}
                  onChange={(event) => setCompanyEmail(event.target.value)}
                  required
                  disabled={submitting}
                />
                <p className="muted field-hint">{t("companyEmailHint")}</p>
              </label>
              <label className="field">
                <span>{t("phoneOptional")}</span>
                <input
                  className="input"
                  value={companyPhone}
                  onChange={(event) => setCompanyPhone(event.target.value)}
                  disabled={submitting}
                />
              </label>
              <button
                type="submit"
                className="button"
                disabled={submitting || !companyName || !companyEmail}
              >
                {submitting ? t("creatingCompany") : t("continue")}
              </button>
            </form>
          ) : (
            <form className="onboarding-form" onSubmit={handleUserSubmit}>
              <label className="field">
                <span>{t("firstName")}</span>
                <input
                  className="input"
                  value={firstName}
                  onChange={(event) => setFirstName(event.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
              <label className="field">
                <span>{t("lastName")}</span>
                <input
                  className="input"
                  value={lastName}
                  onChange={(event) => setLastName(event.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
              <label className="field">
                <span>{t("workEmail")}</span>
                <input
                  className="input"
                  type="email"
                  value={userEmail}
                  onChange={(event) => setUserEmail(event.target.value)}
                  required
                  disabled={submitting}
                />
                <p className="muted field-hint">{t("workEmailHint")}</p>
              </label>
              <label className="field">
                <span>{tCommon("password")}</span>
                <input
                  className="input"
                  type="password"
                  minLength={8}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  disabled={submitting}
                />
                <p className="muted field-hint">{t("passwordHint")}</p>
              </label>
              <label className="field checkbox-field">
                <input
                  type="checkbox"
                  checked={privacyAccepted}
                  onChange={(event) => {
                    setPrivacyAccepted(event.target.checked);
                    if (event.target.checked) {
                      setError(null);
                    }
                  }}
                  disabled={submitting}
                />
                <span>
                  {t("privacyConsentPrefix")}
                  <Link href="/datenschutz" className="link">
                    {t("privacyConsentLink")}
                  </Link>
                  {t("privacyConsentSuffix")}
                </span>
              </label>
              <div className="form-actions spread">
                <button
                  type="button"
                  className="button secondary"
                  disabled={submitting}
                  onClick={() => setStep("company")}
                >
                  {tCommon("back")}
                </button>
                <button
                  type="submit"
                  className="button"
                  disabled={
                    submitting ||
                    !firstName ||
                    !lastName ||
                    !userEmail ||
                    password.length < 8 ||
                    !privacyAccepted
                  }
                >
                  {submitting ? t("creatingAccount") : t("finishSetup")}
                </button>
              </div>
            </form>
          )}

          <p className="muted onboarding-footer">
            {t("alreadyHaveAccount")} <Link href="/login">{t("signIn")}</Link>
          </p>
        </div>
      </section>
    </MarketingShellClient>
  );
}
