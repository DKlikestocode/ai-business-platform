import logging

import httpx

from app.services.service_area.models import Coordinates
from app.services.service_area.plz import extract_postal_code_from_text, lookup_postal_code

logger = logging.getLogger(__name__)

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_USER_AGENT = "AgentPlatform/1.0 (service-area-geocoding)"


def resolve_coordinates_from_text(text: str | None) -> Coordinates | None:
    if text is None or not text.strip():
        return None

    postal_code = extract_postal_code_from_text(text)
    if postal_code is not None:
        coords = lookup_postal_code(postal_code)
        if coords is not None:
            return coords

    return _geocode_free_text(text.strip())


def _geocode_free_text(query: str) -> Coordinates | None:
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                _NOMINATIM_URL,
                params={
                    "q": query,
                    "countrycodes": "de",
                    "format": "json",
                    "limit": 1,
                },
                headers={"User-Agent": _USER_AGENT},
            )
            response.raise_for_status()
            results = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Geocoding failed for query %r: %s", query, exc)
        return None

    if not results:
        return None

    try:
        return Coordinates(
            latitude=float(results[0]["lat"]),
            longitude=float(results[0]["lon"]),
        )
    except (KeyError, TypeError, ValueError):
        return None
