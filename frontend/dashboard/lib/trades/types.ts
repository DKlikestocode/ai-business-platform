import type { CompanyTradeId } from "@/lib/types";

export const COMPANY_TRADE_IDS = ["skh"] as const;

export function isCompanyTradeId(
  value: string | null | undefined,
): value is CompanyTradeId {
  return value === "skh";
}

export function tradeNamespace(
  trade: CompanyTradeId | null | undefined,
  namespace: string,
): string {
  return trade ? `trades.${trade}.${namespace}` : namespace;
}
