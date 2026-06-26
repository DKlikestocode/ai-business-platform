import { describe, expect, it } from "vitest";

import {
  VOICE_MESSAGE_PATH,
  VOICE_WEBHOOK_PATH,
  buildVoiceMessageUrl,
  buildVoiceWebhookUrl,
} from "@/lib/voice-setup";

describe("voice setup urls", () => {
  it("exposes stable public paths", () => {
    expect(VOICE_WEBHOOK_PATH).toBe("/api/v1/public/voice/webhook");
    expect(VOICE_MESSAGE_PATH).toBe("/api/v1/public/voice/message");
  });

  it("builds absolute urls when origin is provided", () => {
    expect(buildVoiceWebhookUrl("https://app.example.com")).toBe(
      "https://app.example.com/api/v1/public/voice/webhook",
    );
    expect(buildVoiceMessageUrl("https://app.example.com")).toBe(
      "https://app.example.com/api/v1/public/voice/message",
    );
  });
});
