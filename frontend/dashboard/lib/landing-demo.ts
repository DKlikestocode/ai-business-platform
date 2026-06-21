import { buildApiUrl } from "@/lib/api-config";
import type { LeadMessageResponse } from "@/lib/types";

export const LANDING_DEMO_MESSAGE_PATH = "/api/v1/public/landing-demo/message";
export const LANDING_DEMO_CONVERSATION_PREFIX = "landing-demo-";
export const LANDING_DEMO_MAX_USER_MESSAGES = 6;

export function createLandingDemoConversationId(): string {
  return `${LANDING_DEMO_CONVERSATION_PREFIX}${Date.now()}`;
}

export function isValidLandingDemoConversationId(conversationId: string): boolean {
  return conversationId.startsWith(LANDING_DEMO_CONVERSATION_PREFIX);
}

export function isLandingDemoLimitStatus(status: number): boolean {
  return status === 429;
}

export class LandingDemoApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "LandingDemoApiError";
    this.status = status;
  }
}

export async function sendLandingDemoMessage(
  payload: {
    conversation_id: string;
    message: string;
  },
): Promise<LeadMessageResponse> {
  const response = await fetch(buildApiUrl(LANDING_DEMO_MESSAGE_PATH), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}.`;
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      try {
        const payload = (await response.json()) as { detail?: string };
        if (typeof payload.detail === "string") {
          detail = payload.detail;
        }
      } catch {
        // keep default detail
      }
    } else {
      const text = await response.text();
      if (text) {
        detail = text;
      }
    }
    throw new LandingDemoApiError(detail, response.status);
  }

  return (await response.json()) as LeadMessageResponse;
}
