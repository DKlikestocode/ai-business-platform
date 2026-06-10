import type { CompanySettings } from "@/lib/types";

export type OnboardingStepId =
  | "company"
  | "user"
  | "notification_email"
  | "copy_widget"
  | "install_widget"
  | "test_widget";

export interface OnboardingStep {
  id: OnboardingStepId;
  title: string;
  description: string;
  href?: string;
  actionLabel?: string;
}

export const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: "company",
    title: "Create company",
    description: "Set up your business profile and tenant slug.",
  },
  {
    id: "user",
    title: "Create first user",
    description: "Add the owner or admin who will manage leads.",
  },
  {
    id: "notification_email",
    title: "Configure notification email",
    description: "Choose where qualified and contactable lead alerts are sent.",
    href: "/settings",
    actionLabel: "Open settings",
  },
  {
    id: "copy_widget",
    title: "Copy widget code",
    description: "Copy the embed snippet for your website.",
    href: "/settings",
    actionLabel: "View embed code",
  },
  {
    id: "install_widget",
    title: "Install widget",
    description: "Paste the snippet before </body> on your site.",
    href: "/settings",
    actionLabel: "Installation guide",
  },
  {
    id: "test_widget",
    title: "Test widget",
    description: "Send a test message and confirm a lead appears in the dashboard.",
    href: "/demo-chat",
    actionLabel: "Open demo chat",
  },
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
  const hasNotificationEmail = Boolean(settings?.notification_email?.trim());

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
