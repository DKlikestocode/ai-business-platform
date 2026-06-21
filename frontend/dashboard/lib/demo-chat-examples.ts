export const DEMO_CHAT_EXAMPLE_KEYS = ["plumber", "roofer", "electrician"] as const;

export type DemoChatExampleKey = (typeof DEMO_CHAT_EXAMPLE_KEYS)[number];

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
  return !candidates.includes(trimmed);
}

export function getDemoChatExampleMessage(
  translate: (key: string) => string,
  key: DemoChatExampleKey,
): string {
  const messageKey = `exampleMessages.${key}`;
  const message = translate(messageKey).trim();
  if (!isResolvedTranslation(message, messageKey)) {
    throw new Error(`Demo chat example message could not be resolved for key: ${key}`);
  }
  return message;
}
