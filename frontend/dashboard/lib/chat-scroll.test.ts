import { describe, expect, it, vi } from "vitest";

import { scrollChatContainerToBottom } from "@/lib/chat-scroll";

describe("scrollChatContainerToBottom", () => {
  it("scrolls the container element, not the document", () => {
    const scrollTo = vi.fn();
    const container = {
      scrollHeight: 480,
      scrollTo,
    } as unknown as HTMLElement;

    scrollChatContainerToBottom(container);

    expect(scrollTo).toHaveBeenCalledWith({
      top: 480,
      behavior: "smooth",
    });
  });

  it("ignores a missing container", () => {
    expect(() => scrollChatContainerToBottom(null)).not.toThrow();
  });
});
