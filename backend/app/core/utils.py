"""Shared utilities."""

import re
import unicodedata


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^\w\s-]", "", ascii_value.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug or "company"
