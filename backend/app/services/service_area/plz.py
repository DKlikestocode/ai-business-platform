import json
import re
from functools import lru_cache
from pathlib import Path

from app.services.service_area.models import Coordinates

_PLZ_PATTERN = re.compile(r"\b(\d{5})\b")
_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "de_plz_centroids.json"


def normalize_postal_code(value: str | None) -> str | None:
    if value is None:
        return None
    digits = re.sub(r"\D", "", value.strip())
    if len(digits) != 5:
        return None
    return digits


def extract_postal_code_from_text(value: str | None) -> str | None:
    if value is None:
        return None
    match = _PLZ_PATTERN.search(value.strip())
    if match is None:
        return None
    return match.group(1)


@lru_cache(maxsize=1)
def _load_centroids() -> dict[str, list[float]]:
    raw = _DATA_PATH.read_text(encoding="utf-8")
    data = json.loads(raw)
    return {str(plz): coords for plz, coords in data.items()}


def lookup_postal_code(postal_code: str) -> Coordinates | None:
    normalized = normalize_postal_code(postal_code)
    if normalized is None:
        return None
    coords = _load_centroids().get(normalized)
    if coords is None or len(coords) != 2:
        return None
    return Coordinates(latitude=coords[0], longitude=coords[1])
