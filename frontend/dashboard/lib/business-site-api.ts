import { buildV1ApiUrl } from "@/lib/api-config";
import type { PublicBusinessSite } from "@/lib/business-site";

export async function fetchPublicBusinessSite(
  companySlug: string,
): Promise<PublicBusinessSite> {
  const response = await fetch(buildV1ApiUrl(`/public/site/${companySlug}`), {
    headers: { Accept: "application/json" },
    next: { revalidate: 300 },
  });

  if (!response.ok) {
    throw new Error(`Failed to load business site for slug: ${companySlug}`);
  }

  return (await response.json()) as PublicBusinessSite;
}
