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


@dataclass
class MockEmailProvider:
    messages: list[EmailMessage] = field(default_factory=list)

    async def send_email(self, message: EmailMessage) -> None:
        self.messages.append(message)


def _qualified_data() -> LeadExtractedData:
    return LeadExtractedData(
        name="Jane Doe",
        phone="555-0100",
        location="Berlin",
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
async def test_notification_skipped_when_qualified_notifications_disabled(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    company.notify_on_new_lead = False
    lead_repository._session.commit()
    lead_repository._session.refresh(company)

    provider = MockEmailProvider()
    service = NotificationService(provider, lead_repository)
    lead = _create_lead(lead_repository, company)

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
    assert "Priorität:" in body
    assert "Lead" not in body
    assert "Kontaktmethode:" in body
    assert f"Im Dashboard anzeigen: http://localhost:3000/leads/{lead.id}" in body


@pytest.mark.asyncio
async def test_contactable_notification_skipped_when_disabled(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    data = LeadExtractedData(
        phone="555-0100",
        description="Leak",
        location="Berlin",
    )
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)
    lead = lead_repository.create(
        company_id=company.id,
        conversation_id=f"notify-conv-{uuid.uuid4().hex[:8]}",
        data=data,
        summary=None,
        qualification=qualification,
    )
    company.notify_on_contactable_lead = False
    lead_repository._session.commit()
    lead_repository._session.refresh(company)

    provider = MockEmailProvider()
    service = NotificationService(provider, lead_repository)

    sent = await service.maybe_notify_lead(company, lead, channel=ConversationChannel.WEB)

    assert sent is False
    assert qualification.qualification_status == QualificationStatus.CONTACTABLE
