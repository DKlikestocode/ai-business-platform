"""HTTP origin validation for widget heartbeat."""

from __future__ import annotations

from urllib.parse import urlparse

_BLOCKED_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "::1", "0.0.0.0"})


class InvalidPageOriginError(ValueError):
    """Raised when page_origin is malformed or not allowed."""


def normalize_page_origin(value: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        raise InvalidPageOriginError("page_origin is required")

    parsed = urlparse(trimmed)
    if parsed.scheme not in ("http", "https"):
        raise InvalidPageOriginError("page_origin must use http or https")
    if not parsed.hostname:
        raise InvalidPageOriginError("page_origin must include a hostname")
    if parsed.username or parsed.password:
        raise InvalidPageOriginError("page_origin must not include credentials")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise InvalidPageOriginError("page_origin must not include a path")

    hostname = parsed.hostname.lower()
    scheme = parsed.scheme.lower()
    port = parsed.port
    if port is None or (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        netloc = hostname
    else:
        netloc = f"{hostname}:{port}"

    return f"{scheme}://{netloc}"


def _origin_from_config_url(value: str) -> str | None:
    trimmed = value.strip()
    if not trimmed:
        return None

    parsed = urlparse(trimmed)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None

    return normalize_page_origin(trimmed)


def build_blocked_origins(
    *,
    public_api_base_url: str,
    frontend_base_url: str | None,
    cors_origins: list[str],
) -> frozenset[str]:
    blocked: set[str] = set()
    for value in [public_api_base_url, frontend_base_url, *cors_origins]:
        if not value:
            continue
        origin = _origin_from_config_url(value)
        if origin is not None:
            blocked.add(origin)
    return frozenset(blocked)


def is_internal_hostname(hostname: str) -> bool:
    host = hostname.lower()
    if host in _BLOCKED_HOSTNAMES:
        return True
    return host.endswith(".localhost")


def validate_widget_page_origin(
    page_origin: str,
    *,
    blocked_origins: frozenset[str],
) -> str:
    normalized = normalize_page_origin(page_origin)
    parsed = urlparse(normalized)
    hostname = parsed.hostname or ""
    if is_internal_hostname(hostname):
        raise InvalidPageOriginError("page_origin is not allowed")
    if normalized in blocked_origins:
        raise InvalidPageOriginError("page_origin is not allowed")
    return normalized
