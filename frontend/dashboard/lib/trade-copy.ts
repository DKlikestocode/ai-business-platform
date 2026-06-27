import { isResolvedTranslation } from "@/lib/demo-chat-examples";

export function translateWithTradeOverride(
  tDefault: (key: string) => string,
  tTrade: (key: string) => string,
  key: string,
  useTrade: boolean,
): string {
  if (!useTrade) {
    return tDefault(key);
  }

  const tradeValue = tTrade(key).trim();
  if (isResolvedTranslation(tradeValue, key)) {
    return tradeValue;
  }

  return tDefault(key);
}
