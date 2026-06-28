import deMessages from "@/messages/de.json";
import enMessages from "@/messages/en.json";

export type BusinessSiteCopy = (typeof deMessages)["businessSite"];

export function getBusinessSiteCopy(locale: "de" | "en" = "de"): BusinessSiteCopy {
  return locale === "en" ? enMessages.businessSite : deMessages.businessSite;
}
