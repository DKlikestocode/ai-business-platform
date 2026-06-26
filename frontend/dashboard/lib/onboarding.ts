import type { CompanySettings } from "@/lib/types";

export type OnboardingStepId =
  | "company"
  | "user"
  | "notification_email"
  | "copy_widget"
  | "install_widget"
  | "test_widget";

export interface OnboardingStepConfig {
  id: OnboardingStepId;
  href?: string;
}

/** @deprecated Use {@link ACTIVATION_CHECKLIST_STEPS} for Getting Started progress. */
export const ONBOARDING_STEPS: OnboardingStepConfig[] = [
  { id: "company" },
  { id: "user" },
  { id: "notification_email", href: "/settings" },
  { id: "copy_widget", href: "/settings" },
  { id: "install_widget", href: "/settings" },
];

const STORAGE_PREFIX = "ai-agent-onboarding";

function storageKey(companyId: string, step: OnboardingStepId): string {
  return `${STORAGE_PREFIX}:${companyId}:${step}`;
}

export function markOnboardingStepComplete(
  companyId: string,
  step: OnboardingStepId,
): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(storageKey(companyId, step), "1");
}

export function isOnboardingStepComplete(
  companyId: string,
  step: OnboardingStepId,
): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  return window.localStorage.getItem(storageKey(companyId, step)) === "1";
}

/** @deprecated Use {@link evaluateActivationChecklist} for setup progress. */
export function evaluateOnboardingProgress(
  companyId: string,
  settings: CompanySettings | null,
  options?: {
    hasUser?: boolean;
    widgetCopied?: boolean;
    widgetInstalled?: boolean;
    widgetTested?: boolean;
  },
): Record<OnboardingStepId, boolean> {
  const hasNotificationEmail = Boolean(
    settings?.notification_email?.trim() || settings?.email?.trim(),
  );

  return {
    company: true,
    user: options?.hasUser ?? true,
    notification_email: hasNotificationEmail,
    copy_widget:
      options?.widgetCopied ??
      isOnboardingStepComplete(companyId, "copy_widget"),
    install_widget:
      options?.widgetInstalled ??
      isOnboardingStepComplete(companyId, "install_widget"),
    test_widget:
      options?.widgetTested ??
      isOnboardingStepComplete(companyId, "test_widget"),
  };
}

export function isOnboardingComplete(
  progress: Record<OnboardingStepId, boolean>,
): boolean {
  return ONBOARDING_STEPS.every((step) => progress[step.id]);
}

export function countCompletedSteps(
  progress: Record<OnboardingStepId, boolean>,
): number {
  return ONBOARDING_STEPS.filter((step) => progress[step.id]).length;
}
