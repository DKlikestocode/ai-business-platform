export interface PublicBusinessSite {
  company_name: string;
  company_slug: string;
  email: string;
  phone: string | null;
  trade: string | null;
  service_area_center: string | null;
  service_radius_km: number | null;
  widget_company_slug: string;
  widget_api_base: string;
  widget_install_token: string;
  widget_title: string;
}

export interface BusinessSiteTradeProfile {
  titleSuffix: string;
  heroKicker: string;
  heroSubline: string;
  services: Array<{ title: string; description: string }>;
  benefits: string[];
  references?: Array<{ title: string; description: string }>;
}

const DEMO_BETRIEB_PROFILE: BusinessSiteTradeProfile = {
  titleSuffix: "Service & Anfragen in Hamburg",
  heroKicker: "Persönlich erreichbar — auch per Chat",
  heroSubline:
    "Ob Termin, Reparatur oder Beratung: Wir nehmen Ihre Anfrage entgegen und melden uns schnell mit den nächsten Schritten. Der Anfragen-Assistent hilft, alles Wichtige direkt festzuhalten.",
  services: [
    {
      title: "Termin & Beratung",
      description:
        "Unverbindliche Erstberatung — per Chat, Telefon oder E-Mail",
    },
    {
      title: "Reparatur & Service",
      description: "Schnelle Hilfe bei akuten Problemen und Wartungsthemen",
    },
    {
      title: "Gewerbe & Privat",
      description: "Für Haushalte und kleine Betriebe in der Region",
    },
    {
      title: "Anfrage per Chat",
      description:
        "Name, Telefon und Anliegen werden strukturiert erfasst — ohne Formular",
    },
  ],
  benefits: [
    "Rückmeldung in der Regel am selben Werktag",
    "Klare Absprachen — ohne Fachchinesisch",
    "Regional in Hamburg-Wandsbek und Umgebung",
    "Chat auch außerhalb der Bürozeiten nutzbar",
  ],
  references: [
    {
      title: "Termin verschieben",
      description: "„Können wir den Termin auf Donnerstag legen?“",
    },
    {
      title: "Angebot anfragen",
      description: "„Was kostet die Reparatur ungefähr?“",
    },
    {
      title: "Dringender Fall",
      description: "„Heute noch jemand vor Ort möglich?“",
    },
  ],
};

export function getBusinessSiteProfile(
  site: Pick<PublicBusinessSite, "company_slug" | "trade">,
): BusinessSiteTradeProfile {
  if (site.company_slug === "demo-betrieb") {
    return DEMO_BETRIEB_PROFILE;
  }
  return getBusinessSiteTradeProfile(site.trade);
}

export function getBusinessSiteTradeProfile(
  trade: string | null | undefined,
): BusinessSiteTradeProfile {
  if (trade === "skh") {
    return {
      titleSuffix: "Sanitär · Heizung · Klima",
      heroKicker: "Ihr SHK-Fachbetrieb",
      heroSubline:
        "Ob Rohrbruch, Heizungsausfall oder Klimaanlage — wir sind für Sie da. Schnell, zuverlässig und aus einer Hand.",
      services: [
        {
          title: "Sanitär",
          description:
            "Verstopfungen, Rohrbruch, Badmodernisierung, Wasserschaden",
        },
        {
          title: "Heizung",
          description: "Störungen, Wartung, Austausch und Energieberatung",
        },
        {
          title: "Klima",
          description: "Installation, Wartung und Reparatur von Klimaanlagen",
        },
        {
          title: "Notfall",
          description:
            "Akute Fälle priorisieren wir — melden Sie sich direkt im Chat",
        },
      ],
      benefits: [
        "Schnelle Rückmeldung — auch abends per Chat möglich",
        "Klare Absprachen vor der Ausführung",
        "Regional verwurzelt und zuverlässig",
        "Sanitär, Heizung und Klima aus einer Hand",
      ],
    };
  }

  return {
    titleSuffix: "Handwerk & Service",
    heroKicker: "Ihr regionaler Fachbetrieb",
    heroSubline:
      "Ob Reparatur, Wartung oder Neuprojekt — wir melden uns schnell und unkompliziert bei Ihnen zurück.",
    services: [
      {
        title: "Beratung",
        description: "Kostenlose Ersteinschätzung zu Ihrem Anliegen",
      },
      {
        title: "Planung",
        description: "Transparente Absprachen vor Ort oder per Chat",
      },
      {
        title: "Ausführung",
        description: "Saubere Arbeit von erfahrenen Fachkräften",
      },
      {
        title: "Service",
        description: "Zuverlässige Erreichbarkeit für Rückfragen",
      },
    ],
    benefits: [
      "Schnelle Rückmeldung — auch abends per Chat möglich",
      "Klare Absprachen vor der Ausführung",
      "Regional verwurzelt und zuverlässig",
      "Persönlicher Ansprechpartner für Ihr Anliegen",
    ],
  };
}

export function formatBusinessSiteServiceArea(
  center: string | null | undefined,
  radiusKm: number | null | undefined,
): string | null {
  const normalizedCenter = center?.trim();
  if (!normalizedCenter) {
    return null;
  }
  if (radiusKm && radiusKm > 0) {
    return `${normalizedCenter} und Umgebung (ca. ${radiusKm} km)`;
  }
  return normalizedCenter;
}

export function normalizePhoneHref(phone: string): string {
  return phone.replace(/[^\d+]/g, "");
}

export const DEMO_BETRIEB_CONTACT_EMAIL = "Dominik.Kessling@gmail.com";

export function getBusinessSiteContactEmail(
  site: Pick<PublicBusinessSite, "company_slug" | "email">,
): string {
  if (site.company_slug === "demo-betrieb") {
    return DEMO_BETRIEB_CONTACT_EMAIL;
  }
  return site.email;
}
