import pytest

from app.services.activation.origin import (
    InvalidPageOriginError,
    build_blocked_origins,
    normalize_page_origin,
    validate_widget_page_origin,
)


def test_normalize_page_origin_strips_default_ports() -> None:
    assert normalize_page_origin("https://www.example.de") == "https://www.example.de"
    assert normalize_page_origin("https://www.example.de:443") == "https://www.example.de"
    assert normalize_page_origin("http://www.example.de:8080") == "http://www.example.de:8080"


def test_normalize_page_origin_rejects_invalid_values() -> None:
    with pytest.raises(InvalidPageOriginError):
        normalize_page_origin("ftp://www.example.de")

    with pytest.raises(InvalidPageOriginError):
        normalize_page_origin("https://www.example.de/path")

    with pytest.raises(InvalidPageOriginError):
        normalize_page_origin("not-a-url")


def test_validate_widget_page_origin_blocks_internal_hosts() -> None:
    blocked = build_blocked_origins(
        public_api_base_url="http://localhost:8000",
        frontend_base_url="http://localhost:3000",
        cors_origins=["http://localhost:3000"],
    )

    with pytest.raises(InvalidPageOriginError):
        validate_widget_page_origin("http://localhost:3000", blocked_origins=blocked)

    with pytest.raises(InvalidPageOriginError):
        validate_widget_page_origin("http://127.0.0.1:4173", blocked_origins=blocked)

    assert (
        validate_widget_page_origin(
            "https://www.kunde-beispiel.de",
            blocked_origins=blocked,
        )
        == "https://www.kunde-beispiel.de"
    )
