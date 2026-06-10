from uuid import UUID

from app.agents.lead_agent.models import LeadStatus, QualificationStatus
from app.agents.lead_agent.repository import LeadRepository
from app.api.schemas.leads import (
    LeadResponse,
    PaginatedLeadResponse,
    build_paginated_response,
    lead_to_response,
)


class LeadDashboardService:
    """Read and update operations for dashboard lead management."""

    def __init__(self, repository: LeadRepository) -> None:
        self._repository = repository

    def list_leads(
        self,
        *,
        page: int,
        page_size: int,
        company_id: UUID,
        status: LeadStatus | None = None,
        qualification_status: QualificationStatus | None = None,
        contactable: bool | None = None,
        sort: str = "created_at_desc",
    ) -> PaginatedLeadResponse:
        items, total = self._repository.list_leads(
            page=page,
            page_size=page_size,
            status=status,
            qualification_status=(
                qualification_status.value if qualification_status is not None else None
            ),
            contactable=contactable,
            sort=sort,
            company_id=company_id,
        )
        return build_paginated_response(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
        )

    def get_lead(self, lead_id: UUID, *, company_id: UUID) -> LeadResponse | None:
        lead = self._repository.get_by_id(lead_id, company_id=company_id)
        if lead is None:
            return None
        return lead_to_response(lead)

    def update_status(
        self,
        lead_id: UUID,
        status: LeadStatus,
        *,
        company_id: UUID,
    ) -> LeadResponse | None:
        lead = self._repository.update_status(lead_id, status, company_id=company_id)
        if lead is None:
            return None
        return lead_to_response(lead)
