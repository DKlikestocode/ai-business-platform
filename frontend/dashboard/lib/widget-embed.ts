export function buildWidgetEmbedSnippet(
  companySlug: string,
  apiBase: string,
): string {
  const base = apiBase.replace(/\/$/, "");
  return `<div
  id="ai-agent-widget"
  data-company-slug="${companySlug}"
  data-api-base="${base}"
  data-title="Chat with us"
></div>
<script src="${base}/static/widget/widget.js"></script>`;
}

export function getPublicApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    return (
      process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
      window.location.origin.replace(/:\d+$/, ":8000")
    );
  }

  return (
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
    "http://localhost:8000"
  );
}
