/** Scroll inside a chat panel only — never move the page viewport. */
export function scrollChatContainerToBottom(
  container: HTMLElement | null,
  behavior: ScrollBehavior = "smooth",
): void {
  if (!container) {
    return;
  }

  container.scrollTo({
    top: container.scrollHeight,
    behavior,
  });
}
