"""Appointment-related helpers for lead capture."""

from app.agents.lead_agent.models import (
    AppointmentConfirmationPreference,
    InquiryKind,
    LeadExtractedData,
)


def is_appointment_inquiry(data: LeadExtractedData) -> bool:
    if data.inquiry_kind == InquiryKind.APPOINTMENT_CONSULTATION:
        return True
    if data.preferred_callback_time and str(data.preferred_callback_time).strip():
        return True
    return False


def has_appointment_time_window(data: LeadExtractedData) -> bool:
    return bool(data.preferred_callback_time and str(data.preferred_callback_time).strip())


def should_ask_appointment_confirmation_preference(data: LeadExtractedData) -> bool:
    # Disabled until SMS/phone appointment confirmation is product-ready.
    return False


def sanitize_appointment_confirmation_preference(
    data: LeadExtractedData,
) -> LeadExtractedData:
    preference = data.appointment_confirmation_preference
    if preference is None:
        return data
    if preference in AppointmentConfirmationPreference:
        return data
    return data.model_copy(update={"appointment_confirmation_preference": None})
