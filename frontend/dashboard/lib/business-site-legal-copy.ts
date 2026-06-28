import type { PublicBusinessSite } from "@/lib/business-site";
import { getBusinessSiteCopy } from "@/lib/business-site-copy";

export type BusinessSiteLegalVariant = "impressum" | "datenschutz";

type LegalSection = {
  heading: string;
  body: string;
};

type LegalPageCopy = {
  title: string;
  intro: string;
  sections: LegalSection[];
};

function replaceTokens(template: string, site: PublicBusinessSite): string {
  return template
    .replaceAll("{companyName}", site.company_name)
    .replaceAll("{email}", site.email)
    .replaceAll("{phone}", site.phone?.trim() || "—");
}

function section(
  heading: string,
  body: string,
  site: PublicBusinessSite,
): LegalSection {
  return {
    heading,
    body: replaceTokens(body, site),
  };
}

export function getBusinessSiteLegalCopy(
  locale: "de" | "en",
  variant: BusinessSiteLegalVariant,
  site: PublicBusinessSite,
): LegalPageCopy {
  const copy = getBusinessSiteCopy(locale);

  if (variant === "impressum") {
    const legal = copy.legal.impressum;
    return {
      title: legal.title,
      intro: replaceTokens(legal.intro, site),
      sections: [
        section(
          legal.sections.operator.heading,
          legal.sections.operator.body,
          site,
        ),
        section(
          legal.sections.contact.heading,
          legal.sections.contact.body,
          site,
        ),
        section(
          legal.sections.dispute.heading,
          legal.sections.dispute.body,
          site,
        ),
      ],
    };
  }

  const legal = copy.legal.datenschutz;
  return {
    title: legal.title,
    intro: replaceTokens(legal.intro, site),
    sections: [
      section(
        legal.sections.controller.heading,
        legal.sections.controller.body,
        site,
      ),
      section(
        legal.sections.dataCollected.heading,
        legal.sections.dataCollected.body,
        site,
      ),
      section(legal.sections.purpose.heading, legal.sections.purpose.body, site),
      section(
        legal.sections.legalBasis.heading,
        legal.sections.legalBasis.body,
        site,
      ),
      section(
        legal.sections.processors.heading,
        legal.sections.processors.body,
        site,
      ),
      section(legal.sections.rights.heading, legal.sections.rights.body, site),
      section(
        legal.sections.changes.heading,
        legal.sections.changes.body,
        site,
      ),
    ],
  };
}
