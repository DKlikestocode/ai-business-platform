from pathlib import Path

import pytest
from app.core.exceptions import LLMServiceError
from app.db.models.company import Company
from app.db.models.intake import IntakeItem
from app.repositories.intake_repository import IntakeRepository
from app.services.intake.models import IntakeExtraction, IntakeStatus, ParsedEmail
from app.services.intake.service import IntakeService

from .conftest import FIXTURE_ROOT, load_expected


class StaticExtractionClient:
    def __init__(self, extraction: IntakeExtraction) -> None:
        self.extraction = extraction
        self.calls = 0

    @property
    def model_name(self) -> str:
        return "test-extractor"

    async def extract(self, email: ParsedEmail) -> IntakeExtraction:
        self.calls += 1
        return self.extraction


class FailingExtractionClient:
    @property
    def model_name(self) -> str:
        return "test-extractor"

    async def extract(self, email: ParsedEmail) -> IntakeExtraction:
        raise LLMServiceError("provider unavailable")


def _raw_email(case_id: str) -> tuple[Path, bytes]:
    directory = FIXTURE_ROOT / "cases" / case_id
    return directory, (directory / "inquiry.eml").read_bytes()


@pytest.fixture
def isolated_intake_queue(db_session) -> None:
    db_session.query(IntakeItem).filter(
        IntakeItem.status.in_(
            [IntakeStatus.RECEIVED.value, IntakeStatus.PROCESSING.value]
        )
    ).update(
        {IntakeItem.status: IntakeStatus.DISCARDED.value},
        synchronize_session=False,
    )
    db_session.commit()


@pytest.mark.asyncio
async def test_ingests_email_pdf_and_applies_extraction(
    intake_repository: IntakeRepository,
    company: Company,
) -> None:
    case_directory, raw_message = _raw_email("case_002")
    extraction = IntakeExtraction.model_validate(
        load_expected(case_directory)["expected"]
    )
    extraction_client = StaticExtractionClient(extraction)
    service = IntakeService(intake_repository, extraction_client)

    result = await service.ingest_email(
        company_id=company.id,
        raw_message=raw_message,
        source_storage_key="companies/test/emails/case_002.eml",
        attachment_storage_keys={
            "leistungsbeschreibung_bad.pdf": "companies/test/pdfs/case_002.pdf"
        },
    )

    assert result.created is True
    assert result.item.status == IntakeStatus.READY.value
    assert result.item.customer_name == "Tobias Hahn"
    assert result.item.service_requested == "Komplette Badsanierung"
    assert result.item.source_storage_key == "companies/test/emails/case_002.eml"
    assert len(result.item.attachments) == 1
    assert result.item.attachments[0].storage_key == "companies/test/pdfs/case_002.pdf"
    assert extraction_client.calls == 1


@pytest.mark.asyncio
async def test_ingestion_is_idempotent_by_message_id(
    intake_repository: IntakeRepository,
    company: Company,
) -> None:
    case_directory, raw_message = _raw_email("case_001")
    extraction = IntakeExtraction.model_validate(
        load_expected(case_directory)["expected"]
    )
    extraction_client = StaticExtractionClient(extraction)
    service = IntakeService(intake_repository, extraction_client)

    first = await service.ingest_email(company_id=company.id, raw_message=raw_message)
    second = await service.ingest_email(company_id=company.id, raw_message=raw_message)

    assert first.created is True
    assert second.created is False
    assert second.item.id == first.item.id
    assert extraction_client.calls == 1


@pytest.mark.asyncio
async def test_marks_uncertain_extraction_for_review(
    intake_repository: IntakeRepository,
    company: Company,
) -> None:
    case_directory, raw_message = _raw_email("case_005")
    extraction = IntakeExtraction.model_validate(
        load_expected(case_directory)["expected"]
    )
    service = IntakeService(intake_repository, StaticExtractionClient(extraction))

    result = await service.ingest_email(company_id=company.id, raw_message=raw_message)

    assert result.item.status == IntakeStatus.NEEDS_REVIEW.value
    assert result.item.needs_human_review is True
    assert result.item.review_reasons == ["Objektadresse und Postleitzahl fehlen."]


@pytest.mark.asyncio
async def test_preserves_item_when_extraction_fails(
    intake_repository: IntakeRepository,
    company: Company,
) -> None:
    _, raw_message = _raw_email("case_003")
    service = IntakeService(intake_repository, FailingExtractionClient())

    result = await service.ingest_email(company_id=company.id, raw_message=raw_message)

    assert result.item.status == IntakeStatus.FAILED.value
    assert result.item.needs_human_review is True
    assert result.item.processing_error is not None
    assert "nicht automatisch ausgewertet" in result.item.processing_error


@pytest.mark.asyncio
async def test_queue_processes_durably_stored_email(
    intake_repository: IntakeRepository,
    company: Company,
    isolated_intake_queue: None,
) -> None:
    case_directory, raw_message = _raw_email("case_002")
    extraction = IntakeExtraction.model_validate(
        load_expected(case_directory)["expected"]
    )
    ingestion_service = IntakeService(intake_repository)
    result = await ingestion_service.ingest_email(
        company_id=company.id,
        raw_message=raw_message,
    )
    worker_service = IntakeService(
        intake_repository,
        StaticExtractionClient(extraction),
    )

    processed = await worker_service.process_next(
        max_attempts=3,
        lease_seconds=300,
    )

    assert processed is True
    assert result.item.status == IntakeStatus.READY.value
    assert result.item.processing_attempts == 1
    document = intake_repository.get_document(result.item.id, company_id=company.id)
    assert document is not None
    assert document.content == raw_message


@pytest.mark.asyncio
async def test_queue_retries_then_marks_item_failed(
    intake_repository: IntakeRepository,
    company: Company,
    isolated_intake_queue: None,
) -> None:
    _, raw_message = _raw_email("case_003")
    ingestion_service = IntakeService(intake_repository)
    result = await ingestion_service.ingest_email(
        company_id=company.id,
        raw_message=raw_message,
    )
    worker_service = IntakeService(intake_repository, FailingExtractionClient())

    assert await worker_service.process_next(max_attempts=2, lease_seconds=300)
    assert result.item.status == IntakeStatus.RECEIVED.value
    assert await worker_service.process_next(max_attempts=2, lease_seconds=300)

    assert result.item.status == IntakeStatus.FAILED.value
    assert result.item.processing_attempts == 2
