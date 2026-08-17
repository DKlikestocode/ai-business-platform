import base64
from types import SimpleNamespace

import pytest
from app.services.intake.email_parser import parse_email
from app.services.intake.extraction import (
    OpenAIIntakeExtractionClient,
    build_input_content,
)
from app.services.intake.models import IntakeExtraction

from .conftest import FIXTURE_ROOT, load_expected


class FakeResponses:
    def __init__(self, output: IntakeExtraction) -> None:
        self.output = output
        self.request: dict | None = None

    async def parse(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(output_parsed=self.output)


class FakeOpenAIClient:
    def __init__(self, output: IntakeExtraction) -> None:
        self.responses = FakeResponses(output)


def test_builds_pdf_input_for_responses_api() -> None:
    case_directory = FIXTURE_ROOT / "cases" / "case_002"
    parsed = parse_email((case_directory / "inquiry.eml").read_bytes())

    content = build_input_content(parsed)

    assert content[0]["type"] == "input_text"
    assert "komplette Badsanierung" in content[0]["text"]
    assert content[1]["type"] == "input_file"
    assert content[1]["filename"] == "leistungsbeschreibung_bad.pdf"
    encoded = content[1]["file_data"].removeprefix("data:application/pdf;base64,")
    assert base64.b64decode(encoded) == parsed.attachments[0].content


@pytest.mark.asyncio
async def test_uses_structured_responses_output() -> None:
    case_directory = FIXTURE_ROOT / "cases" / "case_001"
    expected = IntakeExtraction.model_validate(
        load_expected(case_directory)["expected"]
    )
    fake_client = FakeOpenAIClient(expected)
    client = OpenAIIntakeExtractionClient(
        api_key="test-key",
        model="gpt-test",
        client=fake_client,  # type: ignore[arg-type]
    )

    result = await client.extract(
        parse_email((case_directory / "inquiry.eml").read_bytes())
    )

    assert result == expected
    assert client.model_name == "gpt-test"
    assert fake_client.responses.request is not None
    assert fake_client.responses.request["text_format"] is IntakeExtraction
    assert fake_client.responses.request["model"] == "gpt-test"
