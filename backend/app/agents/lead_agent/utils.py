from app.agents.lead_agent.models import (
    REQUIRED_LEAD_FIELDS,
    LeadCaptureResult,
    LeadExtractedData,
    LeadMessageRequest,
    LeadMessageResponse,
)


def merge_lead_data(
    existing: LeadExtractedData,
    incoming: LeadExtractedData,
) -> LeadExtractedData:
    merged = existing.model_dump()
    for field, value in incoming.model_dump(exclude_none=True).items():
        if value is not None and str(value).strip():
            merged[field] = str(value).strip()
    return LeadExtractedData.model_validate(merged)


def get_missing_fields(data: LeadExtractedData) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_LEAD_FIELDS:
        value = getattr(data, field)
        if value is None or not str(value).strip():
            missing.append(field)
    return missing


def is_lead_complete(data: LeadExtractedData) -> bool:
    return len(get_missing_fields(data)) == 0


def build_message_response(result: LeadCaptureResult) -> LeadMessageResponse:
    return LeadMessageResponse(
        reply=result.reply,
        lead_complete=result.lead_complete,
        missing_fields=result.missing_fields,
        extracted_data=result.extracted_data,
        lead_id=result.lead_id,
        contactable=result.contactable,
        contact_method=result.contact_method,
        lead_score=result.lead_score,
        qualification_status=result.qualification_status,
    )


def load_lead_data_from_context(raw: object) -> LeadExtractedData:
    if isinstance(raw, dict):
        return LeadExtractedData.model_validate(raw)
    return LeadExtractedData()


def serialize_lead_data(data: LeadExtractedData) -> dict[str, str | None]:
    return data.model_dump(mode="json")
