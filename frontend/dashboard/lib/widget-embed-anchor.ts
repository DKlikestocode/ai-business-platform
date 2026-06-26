export const WIDGET_EMBED_SECTION_ID = "widget-embed";

export const SETTINGS_WIDGET_EMBED_HREF = `/settings#${WIDGET_EMBED_SECTION_ID}`;

export function scrollToWidgetEmbedSection(): void {
  if (typeof document === "undefined") {
    return;
  }

  document.getElementById(WIDGET_EMBED_SECTION_ID)?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

export function isWidgetEmbedHashActive(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  return window.location.hash === `#${WIDGET_EMBED_SECTION_ID}`;
}
