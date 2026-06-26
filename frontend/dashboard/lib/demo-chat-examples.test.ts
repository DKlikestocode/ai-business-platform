import { describe, expect, it } from "vitest";

import de from "@/messages/de.json";
import en from "@/messages/en.json";

import {
  DEMO_CHAT_EXAMPLE_KEYS,
  getDemoChatExampleMessage,
  resolveDemoChatExampleMessage,
} from "@/lib/demo-chat-examples";

describe("demo chat example messages", () => {
  it.each(DEMO_CHAT_EXAMPLE_KEYS)("resolves %s in DE and EN catalogs", (key) => {
    const deMessage = resolveDemoChatExampleMessage(de, key);
    const enMessage = resolveDemoChatExampleMessage(en, key);

    expect(deMessage.length).toBeGreaterThan(20);
    expect(enMessage.length).toBeGreaterThan(20);
    expect(deMessage).not.toBe(en.demoChat?.examplePrompts?.[key]);
  });

  it("resolves messages through the demoChat translation namespace", () => {
    const translate = (key: string) => {
      const messages = de.demoChat as Record<string, unknown>;
      const exampleMessages = messages.exampleMessages as Record<string, string>;
      return exampleMessages[key.replace("exampleMessages.", "")];
    };

    expect(getDemoChatExampleMessage(translate, "plumber")).toContain("Klempner");
  });

  it("includes postal codes in example messages", () => {
    for (const key of DEMO_CHAT_EXAMPLE_KEYS) {
      const message = resolveDemoChatExampleMessage(de, key);
      expect(message).toMatch(/PLZ\s*\d{5}|\(\d{5}\)|\d{5}/);
    }
  });
});
