"""Dashboard API schemas."""

from app.api.schemas.leads import (
    LeadResponse,
    LeadStatusUpdateRequest,
    PaginatedLeadResponse,
    build_paginated_response,
    lead_to_response,
)

__all__ = [
    "LeadResponse",
    "LeadStatusUpdateRequest",
    "PaginatedLeadResponse",
    "build_paginated_response",
    "lead_to_response",
]
