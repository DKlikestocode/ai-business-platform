from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.agents.lead_agent.models import InquiryKind, LeadExtractedData, LeadStatus
from app.agents.lead_agent.urgency import urgency_sort_rank_expression
from app.agents.lead_agent.qualification import QualificationResult, evaluate_qualification
from app.db.models.enums import ConversationChannel
from app.db.models.lead import Lead
from app.services.service_area.models import ServiceAreaEvaluation


class LeadRepository:
    """Persistence layer for captured leads."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        company_id: UUID,
        conversation_id: str,
        data: LeadExtractedData,
        summary: str | None,
        qualification: QualificationResult | None = None,
        status: LeadStatus = LeadStatus.NEW,
        service_area: ServiceAreaEvaluation | None = None,
    ) -> Lead:
        resolved_qualification = qualification or evaluate_qualification(
            data,
            channel=ConversationChannel.WEB,
        )
        lead = self._build_lead(
            company_id=company_id,
            conversation_id=conversation_id,
            data=data,
            summary=summary,
            qualification=resolved_qualification,
            status=status,
            service_area=service_area,
        )
        self._session.add(lead)
        if status != LeadStatus.NEW:
            lead.archived_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(lead)
        return lead

    def create_demo(
        self,
        *,
        company_id: UUID,
        conversation_id: str,
        data: LeadExtractedData,
        summary: str | None,
        status: LeadStatus,
        qualification: QualificationResult | None = None,
        service_area: ServiceAreaEvaluation | None = None,
    ) -> Lead:
        return self.create(
            company_id=company_id,
            conversation_id=conversation_id,
            data=data,
            summary=summary,
            qualification=qualification,
            status=status,
            service_area=service_area,
        )

    def save_or_update(
        self,
        *,
        company_id: UUID,
        conversation_id: str,
        data: LeadExtractedData,
        summary: str | None,
        qualification: QualificationResult,
        existing: Lead | None = None,
        service_area: ServiceAreaEvaluation | None = None,
    ) -> tuple[Lead, bool]:
        if existing is not None:
            self._apply_lead_fields(
                existing,
                data=data,
                summary=summary,
                qualification=qualification,
                service_area=service_area,
            )
            self._session.commit()
            self._session.refresh(existing)
            return existing, False

        lead = self.create(
            company_id=company_id,
            conversation_id=conversation_id,
            data=data,
            summary=summary,
            qualification=qualification,
            service_area=service_area,
        )
        return lead, True

    def get_by_id(self, lead_id: UUID, *, company_id: UUID | None = None) -> Lead | None:
        lead = self._session.get(Lead, lead_id)
        if lead is None:
            return None
        if company_id is not None and lead.company_id != company_id:
            return None
        return lead

    def get_by_conversation(
        self,
        conversation_id: str,
        *,
        company_id: UUID | None = None,
    ) -> Lead | None:
        query = self._session.query(Lead).filter(Lead.conversation_id == conversation_id)
        if company_id is not None:
            query = query.filter(Lead.company_id == company_id)
        return query.order_by(Lead.created_at.desc()).first()

    def delete_by_conversation_ids(
        self,
        conversation_ids: frozenset[str] | set[str],
        *,
        company_id: UUID,
    ) -> int:
        if not conversation_ids:
            return 0

        deleted = (
            self._session.query(Lead)
            .filter(Lead.company_id == company_id)
            .filter(Lead.conversation_id.in_(conversation_ids))
            .delete(synchronize_session=False)
        )
        self._session.commit()
        return deleted

    def delete_by_id(self, lead_id: UUID, *, company_id: UUID) -> bool:
        lead = self.get_by_id(lead_id, company_id=company_id)
        if lead is None:
            return False

        self._session.delete(lead)
        self._session.commit()
        return True

    def delete_contacted(
        self,
        *,
        company_id: UUID,
        contactable: bool | None = None,
        inquiry_kind: str | None = None,
    ) -> int:
        query = self._session.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status != LeadStatus.NEW.value,
        )
        if contactable is not None:
            query = query.filter(Lead.contactable == contactable)
        query = self._apply_inquiry_kind_filter(query, inquiry_kind)

        deleted = query.delete(synchronize_session=False)
        self._session.commit()
        return deleted

    @staticmethod
    def _apply_inquiry_kind_filter(query, inquiry_kind: str | None):
        if inquiry_kind == InquiryKind.APPOINTMENT_CONSULTATION.value:
            return query.filter(
                or_(
                    Lead.inquiry_kind.in_(
                        [
                            InquiryKind.APPOINTMENT_CONSULTATION.value,
                            InquiryKind.UNKNOWN.value,
                        ]
                    ),
                    Lead.inquiry_kind.is_(None),
                )
            )
        if inquiry_kind == InquiryKind.QUOTE.value:
            return query.filter(Lead.inquiry_kind == InquiryKind.QUOTE.value)
        return query

    def list_leads(
        self,
        *,
        page: int,
        page_size: int,
        status: LeadStatus | None = None,
        qualification_status: str | None = None,
        contactable: bool | None = None,
        inquiry_kind: str | None = None,
        sort: str = "created_at_desc",
        company_id: UUID | None = None,
        archived: bool = False,
    ) -> tuple[list[Lead], int]:
        query = self._session.query(Lead)
        if company_id is not None:
            query = query.filter(Lead.company_id == company_id)
        if archived:
            query = query.filter(Lead.status != LeadStatus.NEW.value)
        else:
            query = query.filter(Lead.status == LeadStatus.NEW.value)
        if status is not None:
            query = query.filter(Lead.status == status.value)
        if qualification_status is not None:
            query = query.filter(Lead.qualification_status == qualification_status)
        if contactable is not None:
            query = query.filter(Lead.contactable == contactable)
        query = self._apply_inquiry_kind_filter(query, inquiry_kind)

        if sort == "urgency_desc":
            urgency_rank = urgency_sort_rank_expression(Lead.urgency)
            order_by = (urgency_rank.desc(), Lead.created_at.desc())
        else:
            order_by = (Lead.created_at.desc(),)

        total = query.count()
        items = (
            query.order_by(*order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def update_status(
        self,
        lead_id: UUID,
        status: LeadStatus,
        *,
        company_id: UUID,
    ) -> Lead | None:
        lead = self.get_by_id(lead_id, company_id=company_id)
        if lead is None:
            return None

        lead.status = status.value
        if status == LeadStatus.CONTACTED and lead.contacted_at is None:
            lead.contacted_at = datetime.now(UTC)
        if status == LeadStatus.NEW:
            lead.archived_at = None
            lead.contacted_at = None
        elif lead.archived_at is None:
            lead.archived_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(lead)
        return lead

    def restore_lead(self, lead_id: UUID, *, company_id: UUID) -> Lead | None:
        lead = self.get_by_id(lead_id, company_id=company_id)
        if lead is None:
            return None

        lead.status = LeadStatus.NEW.value
        lead.archived_at = None
        lead.contacted_at = None
        self._session.commit()
        self._session.refresh(lead)
        return lead

    def mark_notification_sent(self, lead_id: UUID) -> Lead | None:
        lead = self._session.get(Lead, lead_id)
        if lead is None or lead.notification_sent_at is not None:
            return lead

        lead.notification_sent_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(lead)
        return lead

    def mark_customer_confirmation_sent(self, lead_id: UUID) -> Lead | None:
        lead = self._session.get(Lead, lead_id)
        if lead is None or lead.customer_confirmation_sent_at is not None:
            return lead

        lead.customer_confirmation_sent_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(lead)
        return lead

    @staticmethod
    def _build_lead(
        *,
        company_id: UUID,
        conversation_id: str,
        data: LeadExtractedData,
        summary: str | None,
        qualification: QualificationResult,
        status: LeadStatus,
        service_area: ServiceAreaEvaluation | None = None,
    ) -> Lead:
        lead = Lead(
            company_id=company_id,
            conversation_id=conversation_id,
            name=data.name or "",
            phone=data.phone or "",
            email=data.email,
            company=data.company,
            location=data.location or "",
            postal_code=data.postal_code,
            service_area_status=(
                service_area.status.value if service_area is not None else None
            ),
            service_area_distance_km=(
                service_area.distance_km if service_area is not None else None
            ),
            service_requested=data.service_requested or "",
            description=data.description or "",
            urgency=data.urgency or "",
            preferred_callback_time=data.preferred_callback_time or "",
            status=status.value,
            summary=summary,
            contactable=qualification.contactable,
            contact_method=qualification.contact_method.value,
            lead_score=qualification.lead_score,
            qualification_status=qualification.qualification_status.value,
            inquiry_kind=(
                data.inquiry_kind.value
                if data.inquiry_kind is not None
                else InquiryKind.UNKNOWN.value
            ),
        )
        return lead

    @staticmethod
    def _apply_lead_fields(
        lead: Lead,
        *,
        data: LeadExtractedData,
        summary: str | None,
        qualification: QualificationResult,
        service_area: ServiceAreaEvaluation | None = None,
    ) -> None:
        lead.name = data.name or lead.name
        lead.phone = data.phone or lead.phone
        lead.email = data.email or lead.email
        lead.company = data.company or lead.company
        lead.location = data.location or lead.location
        lead.postal_code = data.postal_code or lead.postal_code
        if service_area is not None:
            lead.service_area_status = service_area.status.value
            lead.service_area_distance_km = service_area.distance_km
        lead.service_requested = data.service_requested or lead.service_requested
        lead.description = data.description or lead.description
        lead.urgency = data.urgency or lead.urgency
        lead.preferred_callback_time = (
            data.preferred_callback_time or lead.preferred_callback_time
        )
        if summary:
            lead.summary = summary
        lead.contactable = qualification.contactable
        lead.contact_method = qualification.contact_method.value
        lead.lead_score = qualification.lead_score
        lead.qualification_status = qualification.qualification_status.value
        if data.inquiry_kind is not None:
            lead.inquiry_kind = data.inquiry_kind.value
