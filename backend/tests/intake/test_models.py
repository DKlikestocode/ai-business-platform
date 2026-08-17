import json

import pytest
from app.services.intake.models import IntakeExtraction
from app.services.intake.service import _csv_safe
from pydantic import ValidationError

from .conftest import FIXTURE_ROOT


def test_all_twenty_reference_extractions_match_schema() -> None:
    rows = [
        json.loads(line)
        for line in (FIXTURE_ROOT / "expected_outputs.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]

    extractions = [IntakeExtraction.model_validate(row["expected"]) for row in rows]

    assert len(extractions) == 20
    assert sum(item.needs_human_review for item in extractions) == 7
    assert sum(item.safety_warning is not None for item in extractions) == 1
    assert sum(item.duplicate_of is not None for item in extractions) == 1


def test_rejects_confidence_outside_zero_to_one() -> None:
    with pytest.raises(ValidationError, match="between 0 and 1"):
        IntakeExtraction(field_confidence={"customer_name": 1.1})


def test_csv_export_neutralizes_spreadsheet_formulas() -> None:
    assert _csv_safe("=HYPERLINK(\"https://example.test\")") == (
        "'=HYPERLINK(\"https://example.test\")"
    )
    assert _csv_safe("Normale Anfrage") == "Normale Anfrage"
