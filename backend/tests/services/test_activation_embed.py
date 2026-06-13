from app.services.activation.embed import build_widget_embed_snippet


def test_build_widget_embed_snippet_includes_slug_token_and_script() -> None:
    snippet = build_widget_embed_snippet(
        company_slug="acme-plumbing",
        api_base="https://api.example.com/",
        install_token="secret-token",
    )

    assert 'data-company-slug="acme-plumbing"' in snippet
    assert 'data-install-token="secret-token"' in snippet
    assert 'data-api-base="https://api.example.com"' in snippet
    assert snippet.endswith(
        '<script src="https://api.example.com/static/widget/widget.js"></script>'
    )
