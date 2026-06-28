from app.scripts.write_pilot_website import build_pilot_website_html


def test_build_pilot_website_html_includes_widget_embed() -> None:
    html = build_pilot_website_html(
        company_slug="acme-plumbing",
        install_token="test-install-token",
        api_base="https://api.example.com",
    )

    assert 'data-company-slug="acme-plumbing"' in html
    assert 'data-install-token="test-install-token"' in html
    assert "https://api.example.com/static/widget/widget.js?v=3" in html
