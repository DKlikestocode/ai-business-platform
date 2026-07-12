"""HTML and plain-text templates for owner lead notification emails."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.lead import Lead

_URGENCY_LABELS = {
    "high": "Hoch",
    "medium": "Mittel",
    "low": "Niedrig",
}


def _escape(value: str | None) -> str:
    return html.escape((value or "").strip() or "—")


def _urgency_label(urgency: str | None) -> str:
    if not urgency:
        return "—"
    return _URGENCY_LABELS.get(urgency.strip().lower(), urgency)


def build_owner_lead_notification(
    *,
    company: Company,
    lead: Lead,
    frontend_base_url: str | None = None,
) -> tuple[str, str]:
    """Return (plain_text, html) for a new inquiry owner notification."""
    summary = lead.summary or lead.description or lead.service_requested or "—"
    fields: list[tuple[str, str]] = [
        ("Name", lead.name or "—"),
        ("Telefon", lead.phone or "—"),
        ("E-Mail", lead.email or "—"),
        ("Standort", lead.location or "—"),
        ("Angefragter Service", lead.service_requested or "—"),
        ("Dringlichkeit", _urgency_label(lead.urgency)),
        ("Terminwunsch", lead.preferred_callback_time or "—"),
        ("Beschreibung", lead.description or "—"),
    ]

    dashboard_url = None
    if frontend_base_url:
        dashboard_url = f"{frontend_base_url.rstrip('/')}/leads/{lead.id}"

    plain_lines = [
        f"Neue Anfrage für {company.name}",
        "",
        summary,
        "",
    ]
    for label, value in fields:
        plain_lines.append(f"{label}: {value}")
    if dashboard_url:
        plain_lines.extend(["", f"Anfrage im Dashboard öffnen: {dashboard_url}"])
    plain_text = "\n".join(plain_lines)

    rows_html = "".join(
        f"""
        <tr>
          <td style="padding:10px 12px 10px 0;color:#6b7280;font-size:14px;vertical-align:top;width:38%;">{_escape(label)}</td>
          <td style="padding:10px 0;font-size:14px;color:#111827;vertical-align:top;">{_escape(value)}</td>
        </tr>"""
        for label, value in fields
    )

    cta_html = ""
    if dashboard_url:
        cta_html = f"""
        <p style="margin:28px 0 0;">
          <a href="{html.escape(dashboard_url)}"
             style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;
                    font-size:15px;font-weight:600;padding:12px 20px;border-radius:8px;">
            Anfrage im Dashboard öffnen
          </a>
        </p>"""

    html_body = f"""<!DOCTYPE html>
<html lang="de">
  <body style="margin:0;padding:0;background:#f6f7f9;font-family:Inter,ui-sans-serif,system-ui,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f6f7f9;padding:32px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                 style="max-width:560px;background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
            <tr>
              <td style="padding:24px 28px 8px;">
                <p style="margin:0 0 6px;font-size:13px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;color:#2563eb;">
                  Neue Anfrage
                </p>
                <h1 style="margin:0;font-size:22px;line-height:1.3;color:#111827;font-weight:700;">
                  {_escape(company.name)}
                </h1>
              </td>
            </tr>
            <tr>
              <td style="padding:8px 28px 20px;">
                <div style="background:#f6f7f9;border:1px solid #e5e7eb;border-radius:10px;padding:16px 18px;">
                  <p style="margin:0;font-size:16px;line-height:1.5;color:#111827;font-weight:600;">
                    {_escape(summary)}
                  </p>
                </div>
              </td>
            </tr>
            <tr>
              <td style="padding:0 28px 24px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                  {rows_html}
                </table>
                {cta_html}
              </td>
            </tr>
            <tr>
              <td style="padding:16px 28px 24px;border-top:1px solid #e5e7eb;">
                <p style="margin:0;font-size:12px;line-height:1.5;color:#9ca3af;">
                  AI Anfragen-Assistent · Benachrichtigung für {_escape(company.name)}
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

    return plain_text, html_body
