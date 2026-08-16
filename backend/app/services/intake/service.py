import csv
import io
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.core.exceptions import LLMServiceError
from app.db.models.intake import IntakeItem
from app.repositories.intake_repository import IntakeRepository
from app.services.intake.email_parser import EmailParseError, parse_email, source_sha256
from app.services.intake.extraction import IntakeExtractionClient
from app.services.intake.models import IntakeReviewDecision, IntakeStatus


@dataclass(frozen=True)
class IntakeIngestionResult:
    item: IntakeItem
    created: bool


class IntakeService:
    def __init__(
        self,
        repository: IntakeRepository,
        extraction_client: IntakeExtractionClient | None = None,
    ) -> None:
        self._repository = repository
        self._extraction_client = extraction_client

    async def ingest_email(
        self,
        *,
        company_id: UUID,
        raw_message: bytes,
        provider_event_id: str | None = None,
        source_storage_key: str | None = None,
        attachment_storage_keys: dict[str, str] | None = None,
    ) -> IntakeIngestionResult:
        email = parse_email(raw_message)
        item, created = self._repository.create_received_email(
            company_id=company_id,
            email=email,
            source_sha256=source_sha256(raw_message),
            raw_message=raw_message,
            provider_event_id=provider_event_id,
            source_storage_key=source_storage_key,
            attachment_storage_keys=attachment_storage_keys,
        )
        if not created or self._extraction_client is None:
            return IntakeIngestionResult(item=item, created=created)

        try:
            extraction = await self._extraction_client.extract(email)
        except LLMServiceError:
            item = self._repository.mark_failed(
                item,
                error="Die Anfrage konnte nicht automatisch ausgewertet werden.",
            )
            return IntakeIngestionResult(item=item, created=True)

        item = self._repository.apply_extraction(
            item,
            extraction=extraction,
            model_name=self._extraction_client.model_name,
        )
        return IntakeIngestionResult(item=item, created=True)

    async def process_next(
        self,
        *,
        max_attempts: int,
        lease_seconds: int,
    ) -> bool:
        if self._extraction_client is None:
            raise RuntimeError("An extraction client is required for queue processing.")

        item = self._repository.claim_next(
            max_attempts=max_attempts,
            lease_seconds=lease_seconds,
        )
        if item is None:
            return False

        document = self._repository.get_document(item.id)
        if document is None:
            self._repository.mark_processing_failure(
                item,
                error="Das Originaldokument fehlt.",
                max_attempts=max_attempts,
            )
            return True

        try:
            email = parse_email(document.content)
        except EmailParseError as exc:
            self._repository.mark_processing_failure(
                item,
                error=str(exc) or "Die Anfrage konnte nicht verarbeitet werden.",
                max_attempts=max_attempts,
            )
            return True
        try:
            extraction = await self._extraction_client.extract(email)
        except LLMServiceError:
            self._repository.mark_processing_failure(
                item,
                error="Die automatische Auswertung ist vorübergehend fehlgeschlagen.",
                max_attempts=max_attempts,
            )
            return True

        self._repository.apply_extraction(
            item,
            extraction=extraction,
            model_name=self._extraction_client.model_name,
        )
        return True

    def get_item(self, item_id: UUID, *, company_id: UUID) -> IntakeItem | None:
        return self._repository.get_by_id(item_id, company_id=company_id)

    def list_items(
        self,
        *,
        company_id: UUID,
        page: int,
        page_size: int,
        status: IntakeStatus | None = None,
    ) -> tuple[list[IntakeItem], int]:
        return self._repository.list_items(
            company_id=company_id,
            page=page,
            page_size=page_size,
            status=status,
        )

    def review_item(
        self,
        item_id: UUID,
        *,
        company_id: UUID,
        fields: dict[str, Any],
        decision: IntakeReviewDecision,
    ) -> IntakeItem | None:
        item = self.get_item(item_id, company_id=company_id)
        if item is None:
            return None
        if item.status not in {
            IntakeStatus.READY.value,
            IntakeStatus.NEEDS_REVIEW.value,
            IntakeStatus.FAILED.value,
            IntakeStatus.EXPORTED.value,
        }:
            raise ValueError("Diese Anfrage kann in ihrem aktuellen Status nicht geprüft werden.")

        if "service_address" in fields and fields["service_address"] is not None:
            address = fields["service_address"]
            if hasattr(address, "model_dump"):
                fields["service_address"] = address.model_dump(mode="json")

        if decision == IntakeReviewDecision.APPROVE:
            requested = fields.get("service_requested", item.service_requested)
            description = fields.get("description", item.description)
            if not (requested or description):
                raise ValueError(
                    "Für die Freigabe wird eine Leistung oder Beschreibung benötigt."
                )
            target_status = IntakeStatus.READY
        elif decision == IntakeReviewDecision.DISCARD:
            target_status = IntakeStatus.DISCARDED
        else:
            target_status = IntakeStatus.NEEDS_REVIEW

        return self._repository.apply_review(
            item,
            fields=fields,
            status=target_status,
        )

    def retry_item(self, item_id: UUID, *, company_id: UUID) -> IntakeItem | None:
        item = self.get_item(item_id, company_id=company_id)
        if item is None:
            return None
        if item.status != IntakeStatus.FAILED.value:
            raise ValueError("Nur fehlgeschlagene Anfragen können erneut versucht werden.")
        return self._repository.retry(item)

    def source_document(self, item_id: UUID, *, company_id: UUID) -> bytes | None:
        document = self._repository.get_document(item_id, company_id=company_id)
        return document.content if document is not None else None

    def attachment_content(
        self,
        attachment_id: UUID,
        *,
        item_id: UUID,
        company_id: UUID,
    ) -> tuple[str, str, bytes] | None:
        attachment = self._repository.get_attachment(
            attachment_id,
            item_id=item_id,
            company_id=company_id,
        )
        if attachment is None:
            return None
        document = self._repository.get_document(item_id, company_id=company_id)
        if document is None:
            return None
        email = parse_email(document.content)
        parsed = next(
            (
                candidate
                for candidate in email.attachments
                if candidate.filename == attachment.filename
                and candidate.sha256 == attachment.sha256
            ),
            None,
        )
        if parsed is None:
            return None
        return attachment.filename, attachment.content_type, parsed.content

    def export_csv(self, item_id: UUID, *, company_id: UUID) -> bytes | None:
        item = self.get_item(item_id, company_id=company_id)
        if item is None:
            return None
        if item.status not in {
            IntakeStatus.READY.value,
            IntakeStatus.EXPORTED.value,
        }:
            raise ValueError("Nur freigegebene Anfragen können exportiert werden.")

        address = item.service_address or {}
        rows = [
            ("Anfrage-ID", str(item.id)),
            ("Eingangskanal", item.channel),
            ("Eingangsdatum", item.received_at.isoformat() if item.received_at else ""),
            ("Betreff", item.subject),
            ("Kundenname", item.customer_name or item.sender_name or ""),
            ("Firma", item.customer_company or ""),
            ("E-Mail", item.customer_email or item.sender_email or ""),
            ("Telefon", item.customer_phone or ""),
            ("Straße", str(address.get("street") or "")),
            ("PLZ", str(address.get("postal_code") or "")),
            ("Ort", str(address.get("city") or "")),
            ("Leistung", item.service_requested or ""),
            ("Beschreibung", item.description or ""),
            ("Dringlichkeit", item.urgency or ""),
            ("Wunschtermin", item.preferred_time or ""),
            ("Empfohlene Aktion", item.recommended_action or ""),
        ]
        output = io.StringIO(newline="")
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(label for label, _value in rows)
        writer.writerow(_csv_safe(value) for _label, value in rows)
        if item.status != IntakeStatus.EXPORTED.value:
            self._repository.mark_exported(item)
        return ("\ufeff" + output.getvalue()).encode("utf-8")


def _csv_safe(value: str) -> str:
    stripped = value.lstrip()
    if stripped.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value
