def build_widget_embed_snippet(
    *,
    company_slug: str,
    api_base: str,
    install_token: str,
    title: str = "Anfrage senden",
) -> str:
    base = api_base.rstrip("/")
    return (
        f'<div\n'
        f'  id="ai-agent-widget"\n'
        f'  data-company-slug="{company_slug}"\n'
        f'  data-api-base="{base}"\n'
        f'  data-install-token="{install_token}"\n'
        f'  data-title="{title}"\n'
        f'></div>\n'
        f'<script src="{base}/static/widget/widget.js"></script>'
    )
