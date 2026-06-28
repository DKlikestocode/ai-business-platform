const DEFAULT_SITE_COMPANY_SLUG = "mikes-sanitarbetrieb";

export function parseSiteHostnames(raw: string | undefined): string[] {
  if (!raw?.trim()) {
    return [];
  }

  return raw
    .split(",")
    .map((value) => value.trim().toLowerCase())
    .filter(Boolean);
}

export function isBusinessSiteHostname(
  host: string | null | undefined,
  configuredHosts: string[],
): boolean {
  if (!host || configuredHosts.length === 0) {
    return false;
  }

  const hostname = host.split(":")[0]?.trim().toLowerCase();
  return Boolean(hostname && configuredHosts.includes(hostname));
}

export function getConfiguredSiteHostnames(): string[] {
  return parseSiteHostnames(
    process.env.SITE_HOSTNAMES ?? process.env.SITE_DOMAIN,
  );
}

export function getSiteCompanySlug(): string {
  return (
    process.env.SITE_COMPANY_SLUG?.trim() ||
    process.env.PILOT_COMPANY_SLUG?.trim() ||
    DEFAULT_SITE_COMPANY_SLUG
  );
}
