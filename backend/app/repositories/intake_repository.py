import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session, selectinload

from app.db.models.intake import IntakeAttachment, IntakeDocument, IntakeItem
from app.db.models.lead import Lead
from app.db.models.enums import ConversationChannel
from app.services.intake.models import (
    IntakeChannel,
    IntakeExtraction,
    IntakeStatus,
    ParsedEmail,
)


class IntakeRepository:
    """Tenant-scoped persistence for channel-neutral incoming requests."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_received_email(
        self,
        *,
        company_id: UUID,
        email: ParsedEmail,
        source_sha256: str,
        raw_message: bytes,
        provider_event_id: str | None = None,
        source_storage_key: str | None = None,
        attachment_storage_keys: dict[str, str] | None = None,
    ) -> tuple[IntakeItem, bool]:
        existing = self.find_existing_email(
            company_id=company_id,
            external_id=email.message_id,
            source_sha256=source_sha256,
            provider_event_id=provider_event_id,
        )
        if existing is not None:
            return existing, False

        storage_keys = attachment_storage_keys or {}
        item = IntakeItem(
            company_id=company_id,
            channel=IntakeChannel.EMAIL.value,
            external_id=email.message_id,
            provider_event_id=provider_event_id,
            status=IntakeStatus.RECEIVED.value,
            subject=email.subject,
            sender_name=email.sender_name,
            sender_email=email.sender_email,
            received_at=email.received_at,
            source_sha256=source_sha256,
            source_storage_key=source_storage_key,
            document=IntakeDocument(
                content_type="message/rfc822",
                size_bytes=len(raw_message),
                content=raw_message,
            ),
            attachments=[
                IntakeAttachment(
                    filename=attachment.filename,
                    content_type=attachment.content_type,
                    size_bytes=attachment.size_bytes,
                    sha256=attachment.sha256,
                    storage_key=storage_keys.get(attachment.filename),
                )
                for attachment in email.attachments
            ],
        )
        self._session.add(item)
        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            existing = self.find_existing_email(
                company_id=company_id,
                external_id=email.message_id,
                source_sha256=source_sha256,
                provider_event_id=provider_event_id,
            )
            if existing is None:
                raise
            return existing, False
        self._session.refresh(item)
        return item, True

    def sync_lead(
        self,
        lead: Lead,
        *,
        conversation_channel: ConversationChannel,
    ) -> IntakeItem | None:
        channel = _intake_channel_for_conversation(conversation_channel)
        if channel is None:
            return None

        item = (
            self._base_query()
            .filter(
                IntakeItem.company_id == lead.company_id,
                IntakeItem.channel == channel.value,
                IntakeItem.external_id == str(lead.id),
            )
            .one_or_none()
        )
        if item is None:
            item = IntakeItem(
                company_id=lead.company_id,
                channel=channel.value,
                external_id=str(lead.id),
                source_sha256=_lead_source_sha256(lead.id),
                created_at=lead.created_at,
            )
            self._session.add(item)

        urgency = _normalize_lead_urgency(lead.urgency)
        inquiry_kind = (
            lead.inquiry_kind
            if lead.inquiry_kind in {"appointment_consultation", "quote"}
            else "other"
        )
        review_reasons = [
            "Aus einer bestehenden digitalen Anfrage übernommen; Angaben vor Export prüfen."
        ]
        if not lead.contactable:
            review_reasons.append("Kontaktmöglichkeit prüfen.")
        if not (lead.service_requested or lead.description):
            review_reasons.append("Gewünschte Leistung oder Beschreibung fehlt.")

        item.status = IntakeStatus.NEEDS_REVIEW.value
        item.subject = (
            lead.service_requested or lead.summary or "Kundenanfrage"
        )[:500]
        item.sender_name = lead.name or None
        item.sender_email = lead.email
        item.received_at = lead.created_at
        item.customer_name = lead.name or None
        item.customer_company = lead.company
        item.customer_email = lead.email
        item.customer_phone = lead.phone or None
        item.service_address = {
            "street": None,
            "postal_code": lead.postal_code,
            "city": lead.location or None,
        }
        item.service_requested = lead.service_requested or None
        item.description = lead.description or lead.summary
        item.urgency = urgency
        item.preferred_time = lead.preferred_callback_time or None
        item.inquiry_kind = inquiry_kind
        item.inquiry_scope = "unclear"
        item.contactable = lead.contactable
        item.needs_human_review = True
        item.review_reasons = review_reasons
        item.recommended_action = _recommended_action_for_lead(
            urgency=urgency,
            inquiry_kind=inquiry_kind,
            contactable=lead.contactable,
        )
        item.field_confidence = {}
        item.processing_error = None
        item.processing_started_at = None
        item.processed_at = datetime.now(UTC)
        item.extracted_data = {
            "source": "lead",
            "lead_id": str(lead.id),
            "conversation_id": lead.conversation_id,
            "qualification_status": lead.qualification_status,
            "lead_score": lead.lead_score,
        }
        self._session.commit()
        self._session.refresh(item)
        return item

    def find_existing_email(
        self,
        *,
        company_id: UUID,
        external_id: str | None,
        source_sha256: str,
        provider_event_id: str | None = None,
    ) -> IntakeItem | None:
        query = self._base_query().filter(
            IntakeItem.company_id == company_id,
            IntakeItem.channel == IntakeChannel.EMAIL.value,
        )
        if external_id:
            by_external_id = query.filter(
                IntakeItem.external_id == external_id
            ).one_or_none()
            if by_external_id is not None:
                return by_external_id
        if provider_event_id:
            by_provider_event = query.filter(
                IntakeItem.provider_event_id == provider_event_id
            ).one_or_none()
            if by_provider_event is not None:
                return by_provider_event
        return query.filter(IntakeItem.source_sha256 == source_sha256).first()

    def apply_extraction(
        self,
        item: IntakeItem,
        *,
        extraction: IntakeExtraction,
        model_name: str,
    ) -> IntakeItem:
        item.status = (
            IntakeStatus.NEEDS_REVIEW.value
            if extraction.needs_human_review
            else IntakeStatus.READY.value
        )
        item.customer_name = extraction.customer_name
        item.customer_company = extraction.company
        item.customer_email = extraction.email
        item.customer_phone = extraction.phone
        item.service_address = extraction.service_address.model_dump(mode="json")
        item.service_requested = extraction.service_requested
        item.description = extraction.description
        item.urgency = extraction.urgency.value
        item.preferred_time = extraction.preferred_time
        item.inquiry_kind = extraction.inquiry_kind.value
        item.inquiry_scope = extraction.inquiry_scope.value
        item.contactable = extraction.contactable
        item.needs_human_review = extraction.needs_human_review
        item.review_reasons = extraction.review_reasons
        item.recommended_action = extraction.recommended_action.value
        item.field_confidence = extraction.field_confidence
        item.safety_warning = extraction.safety_warning
        item.extraction_model = model_name
        item.processing_error = None
        item.processing_started_at = None
        item.processed_at = datetime.now(UTC)
        item.extracted_data = extraction.model_dump(mode="json")
        self._session.commit()
        self._session.refresh(item)
        return item

    def claim_next(
        self,
        *,
        max_attempts: int,
        lease_seconds: int,
    ) -> IntakeItem | None:
        stale_before = datetime.now(UTC) - timedelta(seconds=lease_seconds)
        statement = (
            select(IntakeItem)
            .where(
                or_(
                    IntakeItem.status == IntakeStatus.RECEIVED.value,
                    (
                        (IntakeItem.status == IntakeStatus.PROCESSING.value)
                        & (IntakeItem.processing_started_at < stale_before)
                    ),
                )
            )
            .order_by(IntakeItem.created_at.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        item = self._session.execute(statement).scalar_one_or_none()
        if item is None:
            self._session.rollback()
            return None

        if item.processing_attempts >= max_attempts:
            item.status = IntakeStatus.FAILED.value
            item.processing_started_at = None
            item.processing_error = "Maximale Anzahl Verarbeitungsversuche erreicht."
            item.needs_human_review = True
            self._session.commit()
            return self.claim_next(
                max_attempts=max_attempts,
                lease_seconds=lease_seconds,
            )

        item.status = IntakeStatus.PROCESSING.value
        item.processing_attempts += 1
        item.processing_started_at = datetime.now(UTC)
        item.processing_error = None
        self._session.commit()
        self._session.refresh(item)
        return item

    def mark_processing_failure(
        self,
        item: IntakeItem,
        *,
        error: str,
        max_attempts: int,
    ) -> IntakeItem:
        item.status = (
            IntakeStatus.FAILED.value
            if item.processing_attempts >= max_attempts
            else IntakeStatus.RECEIVED.value
        )
        item.processing_started_at = None
        item.processing_error = error[:2000]
        item.needs_human_review = True
        self._session.commit()
        self._session.refresh(item)
        return item

    def retry(self, item: IntakeItem) -> IntakeItem:
        item.status = IntakeStatus.RECEIVED.value
        item.processing_attempts = 0
        item.processing_started_at = None
        item.processing_error = None
        self._session.commit()
        self._session.refresh(item)
        return item

    def apply_review(
        self,
        item: IntakeItem,
        *,
        fields: dict[str, Any],
        status: IntakeStatus,
    ) -> IntakeItem:
        for key, value in fields.items():
            setattr(item, key, value)
        item.status = status.value
        item.needs_human_review = status == IntakeStatus.NEEDS_REVIEW
        if status == IntakeStatus.READY:
            item.review_reasons = []
            item.processing_error = None
        item.contactable = bool(
            item.customer_email or item.customer_phone or item.sender_email
        )
        self._session.commit()
        self._session.refresh(item)
        return item

    def mark_exported(self, item: IntakeItem) -> IntakeItem:
        item.status = IntakeStatus.EXPORTED.value
        item.exported_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(item)
        return item

    def mark_failed(self, item: IntakeItem, *, error: str) -> IntakeItem:
        item.status = IntakeStatus.FAILED.value
        item.processing_error = error[:2000]
        item.needs_human_review = True
        self._session.commit()
        self._session.refresh(item)
        return item

    def get_by_id(self, item_id: UUID, *, company_id: UUID) -> IntakeItem | None:
        return (
            self._base_query()
            .filter(IntakeItem.id == item_id, IntakeItem.company_id == company_id)
            .one_or_none()
        )

    def get_document(
        self,
        item_id: UUID,
        *,
        company_id: UUID | None = None,
    ) -> IntakeDocument | None:
        query = (
            self._session.query(IntakeDocument)
            .join(IntakeItem, IntakeItem.id == IntakeDocument.intake_item_id)
            .filter(IntakeDocument.intake_item_id == item_id)
        )
        if company_id is not None:
            query = query.filter(IntakeItem.company_id == company_id)
        return query.one_or_none()

    def get_attachment(
        self,
        attachment_id: UUID,
        *,
        item_id: UUID,
        company_id: UUID,
    ) -> IntakeAttachment | None:
        return (
            self._session.query(IntakeAttachment)
            .join(IntakeItem, IntakeItem.id == IntakeAttachment.intake_item_id)
            .filter(
                IntakeAttachment.id == attachment_id,
                IntakeAttachment.intake_item_id == item_id,
                IntakeItem.company_id == company_id,
            )
            .one_or_none()
        )

    def list_items(
        self,
        *,
        company_id: UUID,
        page: int,
        page_size: int,
        status: IntakeStatus | None = None,
    ) -> tuple[list[IntakeItem], int]:
        query = self._base_query().filter(IntakeItem.company_id == company_id)
        if status is not None:
            query = query.filter(IntakeItem.status == status.value)
        total = query.count()
        items = (
            query.order_by(IntakeItem.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def _base_query(self) -> Query[IntakeItem]:
        return self._session.query(IntakeItem).options(
            selectinload(IntakeItem.attachments)
        )


def _intake_channel_for_conversation(
    channel: ConversationChannel,
) -> IntakeChannel | None:
    return {
        ConversationChannel.WEB: IntakeChannel.WEBSITE,
        ConversationChannel.VOICE: IntakeChannel.VOICE,
        ConversationChannel.WHATSAPP: IntakeChannel.WHATSAPP,
    }.get(channel)


def _lead_source_sha256(lead_id: UUID) -> str:
    return hashlib.sha256(f"lead:{lead_id}".encode()).hexdigest()


def _normalize_lead_urgency(value: str) -> str:
    normalized = value.strip().lower()
    return {
        "hoch": "high",
        "high": "high",
        "mittel": "medium",
        "medium": "medium",
        "niedrig": "low",
        "low": "low",
    }.get(normalized, "unknown")


def _recommended_action_for_lead(
    *,
    urgency: str,
    inquiry_kind: str,
    contactable: bool,
) -> str:
    if not contactable:
        return "request_missing_information"
    if urgency == "high":
        return "call_immediately"
    if inquiry_kind == "quote":
        return "prepare_quote"
    return "schedule_visit"
