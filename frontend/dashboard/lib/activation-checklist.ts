import {
  embedSnippetIncludesInstallToken,
  isActivationSetupLive,
} from "@/lib/activation-display";
import { isNotificationRecipientConfigured } from "@/lib/notification-recipient";
import type {
  Company,
  CompanyActivation,
  CompanySettings,
  CurrentUser,
} from "@/lib/types";

export type ActivationChecklistStepId =
  | "company"
  | "user"
  | "notification_email"
  | "copy_widget"
  | "install_widget"
  | "first_website_inquiry";

export interface ActivationChecklistStepConfig {
  id: ActivationChecklistStepId;
  href?: string;
}

export const ACTIVATION_CHECKLIST_STEPS: ActivationChecklistStepConfig[] = [
  { id: "company" },
  { id: "user" },
  { id: "notification_email", href: "/settings" },
  { id: "copy_widget", href: "/settings" },
  { id: "install_widget", href: "/settings" },
  { id: "first_website_inquiry", href: "/leads" },
];

export interface ActivationChecklistInput {
  company: Company | null | undefined;
  user: CurrentUser | null | undefined;
  settings: CompanySettings | null | undefined;
  activation: CompanyActivation | null | undefined;
}

function hasNotificationEmailConfigured(
  settings: CompanySettings | null | undefined,
  activation: CompanyActivation | null | undefined,
): boolean {
  if (activation?.notification_configured) {
    return true;
  }
  return isNotificationRecipientConfigured(settings);
}

function hasServerEmbedSnippet(
  activation: CompanyActivation | null | undefined,
): boolean {
  const snippet = activation?.install?.embed_snippet?.trim();
  if (!snippet) {
    return false;
  }
  return embedSnippetIncludesInstallToken(snippet);
}

export function evaluateActivationChecklist(
  input: ActivationChecklistInput,
): Record<ActivationChecklistStepId, boolean> {
  const notificationConfigured = hasNotificationEmailConfigured(
    input.settings,
    input.activation,
  );

  return {
    company: Boolean(input.company),
    user: Boolean(input.user),
    notification_email: notificationConfigured,
    copy_widget: notificationConfigured && hasServerEmbedSnippet(input.activation),
    install_widget: isActivationSetupLive(input.activation?.status),
    first_website_inquiry: Boolean(input.activation?.first_website_inquiry_at),
  };
}

export function countActivationChecklistSteps(
  progress: Record<ActivationChecklistStepId, boolean>,
): number {
  return ACTIVATION_CHECKLIST_STEPS.filter((step) => progress[step.id]).length;
}

export function isActivationChecklistComplete(
  progress: Record<ActivationChecklistStepId, boolean>,
): boolean {
  return ACTIVATION_CHECKLIST_STEPS.every((step) => progress[step.id]);
}

export function isAwaitingFirstWebsiteInquiry(
  progress: Record<ActivationChecklistStepId, boolean>,
): boolean {
  return progress.install_widget && !progress.first_website_inquiry;
}

export function isAwaitingWebsiteLive(
  progress: Record<ActivationChecklistStepId, boolean>,
  status: CompanyActivation["status"] | null | undefined,
): boolean {
  return (
    status === "awaiting_widget" &&
    progress.company &&
    progress.user &&
    progress.notification_email &&
    progress.copy_widget &&
    !progress.install_widget
  );
}
