export const VOICE_MESSAGE_PATH = "/api/v1/public/voice/message";
export const VOICE_WEBHOOK_PATH = "/api/v1/public/voice/webhook";

export function buildVoiceEndpointUrl(path: string, origin?: string): string {
  if (origin && origin.trim()) {
    return `${origin.replace(/\/$/, "")}${path}`;
  }
  return path;
}

export function buildVoiceWebhookUrl(origin?: string): string {
  return buildVoiceEndpointUrl(VOICE_WEBHOOK_PATH, origin);
}

export function buildVoiceMessageUrl(origin?: string): string {
  return buildVoiceEndpointUrl(VOICE_MESSAGE_PATH, origin);
}
