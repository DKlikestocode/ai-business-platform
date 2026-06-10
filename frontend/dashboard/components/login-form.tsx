"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { AlertBanner } from "@/components/ui/alert-banner";
import { formatUserFacingError } from "@/lib/errors";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, loading, error } = useAuth();
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
      setFormError(formatUserFacingError(err, "Sign in failed. Check your email and password."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card card">
        <h1>Sign in</h1>
        <p className="muted">Access your lead dashboard and pilot workspace.</p>
        <p className="muted onboarding-footer">
          New customer? <Link href="/onboarding">Start your pilot</Link>
        </p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Email</span>
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
            <span>Password</span>
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
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
