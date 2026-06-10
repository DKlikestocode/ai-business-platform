"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { MarketingShell } from "@/components/marketing-shell";
import { AlertBanner } from "@/components/ui/alert-banner";
import { useAuth } from "@/components/auth-provider";
import { registerCompany, registerUser } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";

type Step = "company" | "user";

export function OnboardingForm() {
  const router = useRouter();
  const { login } = useAuth();
  const [step, setStep] = useState<Step>("company");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      setError(formatUserFacingError(err, "Could not create company."));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleUserSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!companyId) {
      setError("Create your company profile first.");
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
      router.replace("/getting-started");
    } catch (err) {
      setError(formatUserFacingError(err, "Could not create your user account."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <MarketingShell>
      <section className="onboarding-section shell">
        <div className="onboarding-card card">
          <p className="eyebrow">New customer onboarding</p>
          <h1>Set up your pilot workspace</h1>
          <p className="muted">
            Step {step === "company" ? "1" : "2"} of 2 —{" "}
            {step === "company"
              ? "Create your company"
              : "Create your admin user"}
          </p>

          <div className="step-indicator" aria-hidden="true">
            <span className={step === "company" ? "step active" : "step done"} />
            <span className={step === "user" ? "step active" : "step"} />
          </div>

          {error ? <AlertBanner>{error}</AlertBanner> : null}

          {step === "company" ? (
            <form className="onboarding-form" onSubmit={handleCompanySubmit}>
              <label className="field">
                <span>Company name</span>
                <input
                  className="input"
                  value={companyName}
                  onChange={(event) => setCompanyName(event.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
              <label className="field">
                <span>Company email</span>
                <input
                  className="input"
                  type="email"
                  value={companyEmail}
                  onChange={(event) => setCompanyEmail(event.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
              <label className="field">
                <span>Phone (optional)</span>
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
                {submitting ? "Creating company..." : "Continue"}
              </button>
            </form>
          ) : (
            <form className="onboarding-form" onSubmit={handleUserSubmit}>
              <label className="field">
                <span>First name</span>
                <input
                  className="input"
                  value={firstName}
                  onChange={(event) => setFirstName(event.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
              <label className="field">
                <span>Last name</span>
                <input
                  className="input"
                  value={lastName}
                  onChange={(event) => setLastName(event.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
              <label className="field">
                <span>Work email</span>
                <input
                  className="input"
                  type="email"
                  value={userEmail}
                  onChange={(event) => setUserEmail(event.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
              <label className="field">
                <span>Password</span>
                <input
                  className="input"
                  type="password"
                  minLength={8}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  disabled={submitting}
                />
              </label>
              <div className="form-actions spread">
                <button
                  type="button"
                  className="button secondary"
                  disabled={submitting}
                  onClick={() => setStep("company")}
                >
                  Back
                </button>
                <button
                  type="submit"
                  className="button"
                  disabled={
                    submitting ||
                    !firstName ||
                    !lastName ||
                    !userEmail ||
                    password.length < 8
                  }
                >
                  {submitting ? "Creating account..." : "Finish setup"}
                </button>
              </div>
            </form>
          )}

          <p className="muted onboarding-footer">
            Already have an account? <Link href="/login">Sign in</Link>
          </p>
        </div>
      </section>
    </MarketingShell>
  );
}
