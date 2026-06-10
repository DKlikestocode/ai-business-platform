/**
 * Browser requests use same-origin relative URLs and are proxied by Next.js
 * to the backend (see next.config.ts rewrites).
 *
 * Server-side requests fall back to the internal Docker/service URL.
 */
export function getApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    return "";
  }

  return (
    process.env.API_INTERNAL_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://localhost:8000"
  );
}

export function buildApiUrl(path: string): string {
  const baseUrl = getApiBaseUrl();
  if (!baseUrl) {
    return path;
  }

  return `${baseUrl.replace(/\/$/, "")}${path}`;
}
