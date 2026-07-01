export const OPEN_GETTING_STARTED_EVENT = "dashboard:open-getting-started";
export const CLOSE_GETTING_STARTED_EVENT = "dashboard:close-getting-started";

export function openGettingStartedOverlay(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(new Event(OPEN_GETTING_STARTED_EVENT));
}

export function closeGettingStartedOverlay(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(new Event(CLOSE_GETTING_STARTED_EVENT));
}
