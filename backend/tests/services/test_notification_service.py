import uuid
from dataclasses import dataclass, field

import pytest

from app.agents.lead_agent.models import LeadExtractedData, QualificationStatus
from app.agents.lead_agent.qualification import evaluate_qualification
from app.agents.lead_agent.repository import LeadRepository
from app.db.models.company import Company
from app.db.models.enums import ConversationChannel
from app.services.notifications.interface import EmailMessage
from app.services.notifications.service import NotificationService
from app.services.notifications.sms_interface import SmsMessage


@dataclass
class MockEmailProvider:
    messages: list[EmailMessage] = field(default_factory=list)

    async def send_email(self, message: EmailMessage) -> None:
        self.messages.append(message)


@dataclass
class MockSmsProvider:
    messages: list[SmsMessage] = field(default_factory=list)

    async def send_sms(self, message: SmsMessage) -> None:
        self.messages.append(message)


def _qualified_data() -> LeadExtractedData:
    return LeadExtractedData(
        name="Jane Doe",
        phone="01701234567",
        location="Berlin",
        postal_code="10115",
        service_requested="Roof repair",
        description="Leak in kitchen",
        urgency="high",
        preferred_callback_time="Tomorrow morning",
    )


def _create_lead(lead_repository: LeadRepository, company: Company):
    data = _qualified_data()
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)
    return lead_repository.create(
        company_id=company.id,
        conversation_id=f"notify-conv-{uuid.uuid4().hex[:8]}",
        data=data,
        summary="Jane needs roof repair.",
        qualification=qualification,
    )


@pytest.mark.asyncio
async def test_notification_sent_when_lead_created(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    provider = MockEmailProvider()
    service = NotificationService(provider, lead_repository)
    lead = _create_lead(lead_repository, company)

    sent = await service.maybe_notify_lead(company, lead, channel=ConversationChannel.WEB)

    assert sent is True
    assert len(provider.messages) == 1
    message = provider.messages[0]
    assert message.to == company.email
    assert "Jane Doe" in message.body
    assert "Anfrage" in message.subject
    assert "Lead" not in message.subject
    assert "Anfrage" in message.body
    assert "Lead" not in message.body
    refreshed = lead_repository.get_by_id(lead.id)
    assert refreshed is not None
    assert refreshed.notification_sent_at is not None


@pytest.mark.asyncio
async def test_notification_not_duplicated(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    provider = MockEmailProvider()
    service = NotificationService(provider, lead_repository)
    lead = _create_lead(lead_repository, company)

    first = await service.maybe_notify_lead(company, lead, channel=ConversationChannel.WEB)
    second = await service.maybe_notify_lead(company, lead, channel=ConversationChannel.WEB)

    assert first is True
    assert second is False
    assert len(provider.messages) == 1


@pytest.mark.asyncio
async def test_notification_skipped_when_urgency_below_minimum(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    company.notification_min_urgency = "high"
    lead_repository._session.commit()
    lead_repository._session.refresh(company)

    data = LeadExtractedData(
        name="Jane Doe",
        phone="01701234567",
        location="Berlin",
        description="Leak in kitchen",
        urgency="medium",
    )
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)
    lead = lead_repository.create(
        company_id=company.id,
        conversation_id=f"notify-conv-{uuid.uuid4().hex[:8]}",
        data=data,
        summary="Jane needs help.",
        qualification=qualification,
    )

    provider = MockEmailProvider()
    service = NotificationService(provider, lead_repository)

    sent = await service.maybe_notify_lead(company, lead, channel=ConversationChannel.WEB)

    assert sent is False
    assert provider.messages == []


@pytest.mark.asyncio
async def test_notification_email_includes_dashboard_link_when_configured(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    provider = MockEmailProvider()
    service = NotificationService(
        provider,
        lead_repository,
        frontend_base_url="http://localhost:3000",
    )
    lead = _create_lead(lead_repository, company)

    await service.maybe_notify_lead(company, lead, channel=ConversationChannel.WEB)

    assert len(provider.messages) == 1
    body = provider.messages[0].body
    assert "Zusammenfassung: Jane needs roof repair." in body
    assert "Qualifizierungsstatus: Qualifiziert" in body
    assert "Priorität:" not in body
    assert "Kontaktierbar:" not in body
    assert "Lead" not in body
    assert "Kontaktmethode:" in body
    assert f"Im Dashboard anzeigen: http://localhost:3000/leads/{lead.id}" in body


@pytest.mark.asyncio
async def test_contactable_notification_skipped_when_disabled(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    data = LeadExtractedData(
        phone="01701234567",
        description="Leak",
        location="Berlin",
        urgency="medium",
    )
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)
    lead = lead_repository.create(
        company_id=company.id,
        conversation_id=f"notify-conv-{uuid.uuid4().hex[:8]}",
        data=data,
        summary=None,
        qualification=qualification,
    )
    company.notification_min_urgency = "high"
    lead_repository._session.commit()
    lead_repository._session.refresh(company)

    provider = MockEmailProvider()
    service = NotificationService(provider, lead_repository)

    sent = await service.maybe_notify_lead(company, lead, channel=ConversationChannel.WEB)

    assert sent is False
    assert qualification.qualification_status == QualificationStatus.CONTACTABLE


@pytest.mark.asyncio
async def test_customer_confirmation_sent_for_qualified_lead(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    email_provider = MockEmailProvider()
    sms_provider = MockSmsProvider()
    service = NotificationService(
        email_provider,
        lead_repository,
        sms_provider=sms_provider,
    )
    lead = _create_lead(lead_repository, company)
    lead.email = "customer@example.com"
    lead_repository._session.commit()
    lead_repository._session.refresh(lead)

    sent = await service.maybe_send_customer_confirmation(company, lead)

    assert sent is True
    assert len(email_provider.messages) == 1
    assert email_provider.messages[0].to == "customer@example.com"
    assert len(sms_provider.messages) == 1
    refreshed = lead_repository.get_by_id(lead.id)
    assert refreshed is not None
    assert refreshed.customer_confirmation_sent_at is not None


@pytest.mark.asyncio
async def test_customer_confirmation_not_duplicated(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    email_provider = MockEmailProvider()
    service = NotificationService(email_provider, lead_repository, sms_provider=MockSmsProvider())
    lead = _create_lead(lead_repository, company)
    lead.email = "customer@example.com"
    lead_repository._session.commit()
    lead_repository._session.refresh(lead)

    first = await service.maybe_send_customer_confirmation(company, lead)
    second = await service.maybe_send_customer_confirmation(company, lead)

    assert first is True
    assert second is False
    assert len(email_provider.messages) == 1


@pytest.mark.asyncio
async def test_appointment_confirmation_email_sent_once(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    provider = MockEmailProvider()
    service = NotificationService(provider, lead_repository)
    lead = _create_lead(lead_repository, company)
    lead.email = "customer@example.com"
    lead.preferred_callback_time = "Morgen Vormittag"
    lead_repository._session.commit()
    lead_repository._session.refresh(lead)

    first = await service.send_appointment_confirmation_email(company, lead)
    second = await service.send_appointment_confirmation_email(company, lead)

    assert first is not None
    assert second == first
    assert len(provider.messages) == 1
    assert "Terminbestätigung" in provider.messages[0].subject
    refreshed = lead_repository.get_by_id(lead.id)
    assert refreshed is not None
    assert refreshed.appointment_confirmation_sent_at is not None
