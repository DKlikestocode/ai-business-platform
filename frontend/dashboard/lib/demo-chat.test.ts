import { describe, expect, it } from "vitest";

import { createDemoChatConversationId } from "@/components/demo-chat";

describe("demo chat conversation ids", () => {
  it("generates a non-stable demo-chat id instead of reusing demo-chat-001", () => {
    const conversationId = createDemoChatConversationId();

    expect(conversationId).toMatch(/^demo-chat-\d+$/);
    expect(conversationId).not.toBe("demo-chat-001");
  });
});
