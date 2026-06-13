import { describe, expect, it } from "vitest";

import { activationRefreshLabel } from "@/components/activation-status-view";
import de from "@/messages/de.json";
import en from "@/messages/en.json";
import { isActivationChecklistComplete, evaluateActivationChecklist } from "@/lib/activation-checklist";
import type { CompanyActivation } from "@/lib/types";

function buildActivation(
  status: CompanyActivation["status"],
): CompanyActivation {
  return {
    status,
    notification_configured: true,
    website_url: null,
    widget_live_at: "2026-06-01T10:00:00.000Z",
    widget_last_seen_at: "2026-06-01T10:00:00.000Z",
    widget_last_origin: "https://acme.co",
    install: {
      company_slug: "acme",
      embed_snippet: '<div data-install-token="secret"></div>',
    },
    updated_at: "2026-06-10T12:00:00Z",
  };
}

describe("activation stale owner copy", () => {
  it("includes German stale status and guidance copy", () => {
    expect(de.activation.status.stale).toBe(
      "Der Chat wurde länger nicht auf Ihrer Website gesehen.",
    );
    expect(de.activation.staleGuidance).toBe(
      "Öffnen Sie Ihre Website einmal im Browser.",
    );
    expect(de.activation.refreshStale).toBe("Status erneut prüfen");
  });

  it("includes English stale status and guidance copy", () => {
    expect(en.activation.status.stale).toContain("not been seen");
    expect(en.activation.staleGuidance).toContain("Open your website");
    expect(en.activation.refreshStale).toBe("Check status again");
  });

  it("uses stale-specific refresh label", () => {
    expect(
      activationRefreshLabel("stale", {
        refresh: "Refresh status",
        refreshStale: "Check status again",
      }),
    ).toBe("Check status again");
    expect(
      activationRefreshLabel("live", {
        refresh: "Refresh status",
        refreshStale: "Check status again",
      }),
    ).toBe("Refresh status");
  });
});

describe("activation stale checklist", () => {
  it("does not count stale activation as setup complete", () => {
    const progress = evaluateActivationChecklist({
      company: {
        id: "company-1",
        name: "Acme",
        slug: "acme",
        email: "hello@acme.co",
        phone: null,
        created_at: "2026-06-10T12:00:00Z",
      },
      user: {
        id: "user-1",
        company_id: "company-1",
        first_name: "Alex",
        last_name: "Owner",
        email: "alex@acme.co",
        role: "owner",
        is_active: true,
        created_at: "2026-06-10T12:00:00Z",
      },
      settings: {
        name: "Acme",
        slug: "acme",
        email: "hello@acme.co",
        phone: null,
        notification_email: "alerts@acme.co",
        notify_on_new_lead: true,
        notify_on_contactable_lead: true,
        contactable_lead_notification_threshold: 50,
        created_at: "2026-06-10T12:00:00Z",
      },
      activation: buildActivation("stale"),
    });

    expect(progress.install_widget).toBe(false);
    expect(isActivationChecklistComplete(progress)).toBe(false);
  });
});
