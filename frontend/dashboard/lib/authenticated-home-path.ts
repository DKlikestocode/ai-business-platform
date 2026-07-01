import { shouldShowGettingStartedNav } from "@/lib/activation-checklist";
import {
  loadCachedCompanyActivation,
  loadCachedCompanySettings,
} from "@/lib/dashboard-cache";
import type { Company, CurrentUser } from "@/lib/types";

export type AuthenticatedHomePath = "/getting-started" | "/leads";

export async function resolveAuthenticatedHomePath(
  user: CurrentUser,
  company: Company,
): Promise<AuthenticatedHomePath> {
  const [settings, activation] = await Promise.all([
    loadCachedCompanySettings(),
    loadCachedCompanyActivation(),
  ]);

  if (
    shouldShowGettingStartedNav({
      company,
      user,
      settings,
      activation,
    })
  ) {
    return "/getting-started";
  }

  return "/leads";
}
