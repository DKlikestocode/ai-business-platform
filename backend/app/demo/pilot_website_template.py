"""Static pilot marketing page for a trades / service business website."""

from __future__ import annotations

import html
from dataclasses import dataclass


@dataclass(frozen=True)
class PilotWebsiteContent:
    company_name: str
    trade: str | None
    email: str
    phone: str | None
    service_area_center: str | None
    service_radius_km: int | None
    widget_snippet: str


def _skh_profile() -> dict[str, object]:
    return {
        "title_suffix": "Sanitär · Heizung · Klima",
        "hero_kicker": "Ihr SHK-Fachbetrieb",
        "hero_subline": (
            "Ob Rohrbruch, Heizungsausfall oder Klimaanlage — "
            "wir sind für Sie da. Schnell, zuverlässig und aus einer Hand."
        ),
        "services": [
            ("Sanitär", "Verstopfungen, Rohrbruch, Badmodernisierung, Wasserschaden"),
            ("Heizung", "Störungen, Wartung, Austausch und Energieberatung"),
            ("Klima", "Installation, Wartung und Reparatur von Klimaanlagen"),
            ("Notfall", "Akute Fälle priorisieren wir — melden Sie sich direkt im Chat"),
        ],
        "benefits": [
            "Schnelle Rückmeldung — auch abends per Chat möglich",
            "Klare Absprachen vor der Ausführung",
            "Regional verwurzelt und zuverlässig",
            "Sanitär, Heizung und Klima aus einer Hand",
        ],
    }


def _general_profile() -> dict[str, object]:
    return {
        "title_suffix": "Handwerk & Service",
        "hero_kicker": "Ihr regionaler Fachbetrieb",
        "hero_subline": (
            "Ob Reparatur, Wartung oder Neuprojekt — wir melden uns schnell "
            "und unkompliziert bei Ihnen zurück."
        ),
        "services": [
            ("Beratung", "Kostenlose Ersteinschätzung zu Ihrem Anliegen"),
            ("Planung", "Transparente Absprachen vor Ort oder per Chat"),
            ("Ausführung", "Saubere Arbeit von erfahrenen Fachkräften"),
            ("Service", "Zuverlässige Erreichbarkeit für Rückfragen"),
        ],
        "benefits": [
            "Schnelle Rückmeldung — auch abends per Chat möglich",
            "Klare Absprachen vor der Ausführung",
            "Regional verwurzelt und zuverlässig",
            "Persönlicher Ansprechpartner für Ihr Anliegen",
        ],
    }


def _trade_profile(trade: str | None) -> dict[str, object]:
    if trade == "skh":
        return _skh_profile()
    return _general_profile()


def _service_area_label(center: str | None, radius_km: int | None) -> str | None:
    center = (center or "").strip()
    if not center:
        return None
    if radius_km and radius_km > 0:
        return f"{center} und Umgebung (ca. {radius_km} km)"
    return center


def build_pilot_website_html(content: PilotWebsiteContent) -> str:
    profile = _trade_profile(content.trade)
    company_name = html.escape(content.company_name.strip() or "Ihr Fachbetrieb")
    title_suffix = html.escape(str(profile["title_suffix"]))
    hero_kicker = html.escape(str(profile["hero_kicker"]))
    hero_subline = html.escape(str(profile["hero_subline"]))
    email = html.escape(content.email.strip())
    phone_raw = (content.phone or "").strip()
    phone = html.escape(phone_raw)
    phone_href = "".join(ch for ch in phone_raw if ch.isdigit() or ch == "+")
    service_area = _service_area_label(
        content.service_area_center,
        content.service_radius_km,
    )
    service_area_html = (
        f'<p class="service-area">{html.escape(service_area)}</p>' if service_area else ""
    )

    services_html = "\n".join(
        f"""          <article class="service-card">
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(description)}</p>
          </article>"""
        for title, description in profile["services"]  # type: ignore[attr-defined]
    )
    benefits_html = "\n".join(
        f"            <li>{html.escape(item)}</li>"
        for item in profile["benefits"]  # type: ignore[attr-defined]
    )

    phone_block = (
        f'<a class="header-phone" href="tel:{phone_href}">{phone}</a>'
        if phone_raw
        else ""
    )
    contact_phone = (
        f'<p><strong>Telefon:</strong> <a href="tel:{phone_href}">{phone}</a></p>'
        if phone_raw
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{company_name} — {title_suffix}. Jetzt Anfrage stellen per Chat oder E-Mail." />
  <title>{company_name} | {title_suffix}</title>
  <style>
    :root {{
      --primary: #1d4ed8;
      --primary-dark: #1e3a8a;
      --text: #111827;
      --muted: #4b5563;
      --border: #e5e7eb;
      --surface: #ffffff;
      --bg: #f8fafc;
      --accent: #eff6ff;
      --shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
      --radius: 14px;
      --max: 1120px;
    }}

    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background: var(--bg);
      line-height: 1.6;
    }}

    a {{ color: var(--primary); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}

    .container {{
      width: min(100% - 2rem, var(--max));
      margin-inline: auto;
    }}

    .site-header {{
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--border);
    }}

    .header-inner {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 1rem 0;
      flex-wrap: wrap;
    }}

    .brand {{
      display: flex;
      flex-direction: column;
      gap: 0.15rem;
    }}

    .brand strong {{
      font-size: 1.05rem;
      letter-spacing: -0.02em;
    }}

    .brand span {{
      color: var(--muted);
      font-size: 0.85rem;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}

    .header-phone {{
      font-weight: 600;
      color: var(--text);
      white-space: nowrap;
    }}

    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 44px;
      padding: 0.7rem 1.1rem;
      border-radius: 999px;
      border: none;
      background: var(--primary);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      box-shadow: 0 8px 24px rgba(29, 78, 216, 0.22);
    }}

    .button:hover {{
      background: var(--primary-dark);
      text-decoration: none;
    }}

    .button.secondary {{
      background: #fff;
      color: var(--primary);
      border: 1px solid var(--border);
      box-shadow: none;
    }}

    .hero {{
      padding: 4.5rem 0 3.5rem;
    }}

    .hero-grid {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 2rem;
      align-items: center;
    }}

    .hero-card {{
      background: linear-gradient(135deg, #ffffff 0%, #eff6ff 100%);
      border: 1px solid var(--border);
      border-radius: calc(var(--radius) + 6px);
      padding: 2rem;
      box-shadow: var(--shadow);
    }}

    .eyebrow {{
      display: inline-block;
      margin-bottom: 0.75rem;
      padding: 0.35rem 0.7rem;
      border-radius: 999px;
      background: var(--accent);
      color: var(--primary-dark);
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0 0 1rem;
      font-size: clamp(2rem, 4vw, 3.2rem);
      line-height: 1.08;
      letter-spacing: -0.03em;
    }}

    .hero p {{
      margin: 0;
      color: var(--muted);
      font-size: 1.05rem;
      max-width: 38rem;
    }}

    .hero-actions {{
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-top: 1.5rem;
    }}

    .hero-panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.5rem;
      box-shadow: var(--shadow);
    }}

    .hero-panel h2 {{
      margin: 0 0 0.75rem;
      font-size: 1.1rem;
    }}

    .checklist {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 0.75rem;
    }}

    .checklist li {{
      display: flex;
      gap: 0.65rem;
      align-items: flex-start;
      color: var(--muted);
    }}

    .checklist li::before {{
      content: "✓";
      color: var(--primary);
      font-weight: 700;
      margin-top: 0.05rem;
    }}

    .section {{
      padding: 3.5rem 0;
    }}

    .section-header {{
      margin-bottom: 1.75rem;
      max-width: 42rem;
    }}

    .section-header h2 {{
      margin: 0 0 0.5rem;
      font-size: clamp(1.5rem, 3vw, 2rem);
      letter-spacing: -0.02em;
    }}

    .section-header p {{
      margin: 0;
      color: var(--muted);
    }}

    .services-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 1rem;
    }}

    .service-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem;
      min-height: 100%;
    }}

    .service-card h3 {{
      margin: 0 0 0.5rem;
      font-size: 1.05rem;
    }}

    .service-card p {{
      margin: 0;
      color: var(--muted);
      font-size: 0.95rem;
    }}

    .trust-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 1rem;
    }}

    .trust-item {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem;
      text-align: center;
    }}

    .trust-item strong {{
      display: block;
      margin-bottom: 0.35rem;
      font-size: 1rem;
    }}

    .trust-item span {{
      color: var(--muted);
      font-size: 0.92rem;
    }}

    .contact-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: calc(var(--radius) + 4px);
      padding: 2rem;
      box-shadow: var(--shadow);
      display: grid;
      gap: 1rem;
    }}

    .contact-card p {{
      margin: 0;
      color: var(--muted);
    }}

    .service-area {{
      margin: 0;
      color: var(--primary-dark);
      font-weight: 600;
    }}

    .site-footer {{
      border-top: 1px solid var(--border);
      background: #0f172a;
      color: #cbd5e1;
      padding: 2rem 0;
      margin-top: 1rem;
    }}

    .footer-inner {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
      align-items: flex-start;
    }}

    .footer-inner strong {{
      color: #fff;
      display: block;
      margin-bottom: 0.35rem;
    }}

    .footer-inner p {{
      margin: 0;
      font-size: 0.92rem;
    }}

    @media (max-width: 960px) {{
      .hero-grid,
      .services-grid,
      .trust-strip {{
        grid-template-columns: 1fr 1fr;
      }}
    }}

    @media (max-width: 720px) {{
      .hero {{
        padding-top: 3rem;
      }}

      .hero-grid,
      .services-grid,
      .trust-strip {{
        grid-template-columns: 1fr;
      }}

      .header-inner {{
        align-items: flex-start;
      }}
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <div class="brand">
        <strong>{company_name}</strong>
        <span>{title_suffix}</span>
      </div>
      <div class="header-actions">
        {phone_block}
        <a class="button" href="#kontakt">Anfrage stellen</a>
      </div>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="container hero-grid">
        <div class="hero-card">
          <span class="eyebrow">{hero_kicker}</span>
          <h1>{company_name}</h1>
          <p>{hero_subline}</p>
          <div class="hero-actions">
            <a class="button" href="#kontakt">Jetzt Anfrage senden</a>
            <a class="button secondary" href="#leistungen">Leistungen ansehen</a>
          </div>
        </div>
        <aside class="hero-panel" aria-label="Ihre Vorteile">
          <h2>Warum Kunden uns wählen</h2>
          <ul class="checklist">
{benefits_html}
          </ul>
        </aside>
      </div>
    </section>

    <section class="section" id="leistungen">
      <div class="container">
        <div class="section-header">
          <h2>Unsere Leistungen</h2>
          <p>Von der schnellen Hilfe im Notfall bis zur geplanten Modernisierung — wir kümmern uns um Ihr Anliegen.</p>
        </div>
        <div class="services-grid">
{services_html}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="trust-strip">
          <div class="trust-item">
            <strong>Schnelle Hilfe</strong>
            <span>Notfälle nehmen wir ernst und melden uns zeitnah zurück.</span>
          </div>
          <div class="trust-item">
            <strong>Faire Beratung</strong>
            <span>Transparente Kommunikation — ohne Fachchinesisch.</span>
          </div>
          <div class="trust-item">
            <strong>Regional vor Ort</strong>
            <span>{html.escape(service_area) if service_area else "Wir sind in Ihrer Nähe für Sie da."}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="kontakt">
      <div class="container">
        <div class="section-header">
          <h2>Kontakt & Anfrage</h2>
          <p>Beschreiben Sie Ihr Anliegen im Chat unten rechts — wir melden uns mit den wichtigsten nächsten Schritten.</p>
        </div>
        <div class="contact-card">
          <p><strong>E-Mail:</strong> <a href="mailto:{email}">{email}</a></p>
          {contact_phone}
          {service_area_html}
          <p>Öffnen Sie den Chat unten rechts und schildern Sie kurz Ihr Problem, Ihre Postleitzahl und wie wir Sie erreichen können.</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        <strong>{company_name}</strong>
        <p>{title_suffix}</p>
      </div>
      <div>
        <p>E-Mail: <a href="mailto:{email}">{email}</a></p>
        {f"<p>Telefon: <a href='tel:{phone_href}'>{phone}</a></p>" if phone_raw else ""}
        <p>© {company_name}</p>
      </div>
    </div>
  </footer>

  {content.widget_snippet}
</body>
</html>
"""
