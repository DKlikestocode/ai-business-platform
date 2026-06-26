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

  it("builds absolute urls from api base", () => {
    expect(buildVoiceWebhookUrl("http://localhost:8000")).toBe(
      "http://localhost:8000/api/v1/public/voice/webhook",
    );
    expect(buildVoiceMessageUrl("https://api.example.com")).toBe(
      "https://api.example.com/api/v1/public/voice/message",
    );
  });
});
