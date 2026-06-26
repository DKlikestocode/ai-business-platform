from dataclasses import dataclass
from enum import StrEnum


class ServiceAreaStatus(StrEnum):
    NOT_CONFIGURED = "not_configured"
    UNKNOWN = "unknown"
    IN_RANGE = "in_range"
    OUT_OF_RANGE = "out_of_range"


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class ServiceAreaEvaluation:
    status: ServiceAreaStatus
    distance_km: float | None = None
    postal_code: str | None = None
