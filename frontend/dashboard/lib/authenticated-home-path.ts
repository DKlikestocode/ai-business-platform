import { resolveAuthenticatedHomePathFromCache } from "@/lib/dashboard-nav";
import {
  loadCachedCompanyActivation,
  loadCachedCompanySettings,
} from "@/lib/dashboard-cache";
import type { Company, CurrentUser } from "@/lib/types";

export type { AuthenticatedHomePath } from "@/lib/dashboard-nav";

export async function resolveAuthenticatedHomePath(
  user: CurrentUser,
  company: Company,
) {
  await Promise.all([
    loadCachedCompanySettings(),
    loadCachedCompanyActivation(),
  ]);

  return resolveAuthenticatedHomePathFromCache(user, company);
}
