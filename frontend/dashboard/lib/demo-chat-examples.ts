import type { CompanyTradeId } from "@/lib/types";

export const DEMO_CHAT_EXAMPLE_KEYS = ["plumber", "roofer", "electrician"] as const;

export const SKH_DEMO_CHAT_EXAMPLE_KEYS = ["heating", "plumbing", "climate"] as const;

export type DemoChatExampleKey = (typeof DEMO_CHAT_EXAMPLE_KEYS)[number];

export type SkhDemoChatExampleKey = (typeof SKH_DEMO_CHAT_EXAMPLE_KEYS)[number];

export type TradeDemoChatExampleKey = DemoChatExampleKey | SkhDemoChatExampleKey;

export function getDemoChatExampleKeys(
  trade: CompanyTradeId | null | undefined,
): readonly TradeDemoChatExampleKey[] {
  if (trade === "skh") {
    return SKH_DEMO_CHAT_EXAMPLE_KEYS;
  }
  return DEMO_CHAT_EXAMPLE_KEYS;
}

type DemoChatMessages = {
  demoChat?: {
    exampleMessages?: Partial<Record<DemoChatExampleKey, string>>;
  };
};

export function resolveDemoChatExampleMessage(
  messages: DemoChatMessages,
  key: DemoChatExampleKey,
): string {
  const message = messages.demoChat?.exampleMessages?.[key]?.trim();
  if (!message) {
    throw new Error(`Missing demo chat example message for key: ${key}`);
  }
  return message;
}

export function isResolvedTranslation(
  value: string,
  key: string,
  namespace = "demoChat",
): boolean {
  const trimmed = value.trim();
  if (!trimmed) {
    return false;
  }

  const candidates = [
    key,
    `${namespace}.${key}`,
    `demoChat.${key}`,
  ];
  if (candidates.includes(trimmed)) {
    return false;
  }
  if (trimmed.endsWith(`.${key}`) && trimmed.includes(".")) {
    return false;
  }
  return true;
}

export function getDemoChatExampleMessage(
  translate: (key: string) => string,
  key: TradeDemoChatExampleKey,
): string {
  const messageKey = `exampleMessages.${key}`;
  const message = translate(messageKey).trim();
  if (!isResolvedTranslation(message, messageKey)) {
    throw new Error(`Demo chat example message could not be resolved for key: ${key}`);
  }
  return message;
}
