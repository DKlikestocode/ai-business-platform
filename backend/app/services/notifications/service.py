import logging

from app.agents.lead_agent.models import QualificationStatus
from app.agents.lead_agent.repository import LeadRepository
from app.db.models.company import Company
from app.db.models.enums import ConversationChannel
from app.db.models.lead import Lead
from app.services.notifications.interface import EmailMessage, EmailProvider

logger = logging.getLogger(__name__)


class NotificationService:
    """Coordinates outbound lead notifications."""

    def __init__(
        self,
        provider: EmailProvider,
        lead_repository: LeadRepository,
        *,
        frontend_base_url: str | None = None,
    ) -> None:
        self._provider = provider
        self._lead_repository = lead_repository
        self._frontend_base_url = frontend_base_url

    def should_notify_lead(
        self,
        company: Company,
        lead: Lead,
        *,
        channel: ConversationChannel,
    ) -> bool:
        if lead.notification_sent_at is not None:
            return False

        if lead.qualification_status == QualificationStatus.QUALIFIED.value:
            return company.notify_on_new_lead

        contactable_allowed = lead.contactable or channel == ConversationChannel.WHATSAPP
        if not contactable_allowed:
            return False

        if not company.notify_on_contactable_lead:
            return False

        return lead.lead_score >= company.contactable_lead_notification_threshold

    async def maybe_notify_lead(
        self,
        company: Company,
        lead: Lead,
        *,
        channel: ConversationChannel,
    ) -> bool:
        if not self.should_notify_lead(company, lead, channel=channel):
            logger.info(
                "Skipping lead notification for lead %s (status=%s, score=%s).",
                lead.id,
                lead.qualification_status,
                lead.lead_score,
            )
            return False

        recipient = company.notification_email or company.email
        if not recipient:
            logger.warning(
                "Skipping lead notification for company %s: no notification email configured.",
                company.id,
            )
            return False

        subject = (
            f"New qualified lead: {lead.name}"
            if lead.qualification_status == QualificationStatus.QUALIFIED.value
            else f"New contactable lead: {lead.name}"
        )
        message = EmailMessage(
            to=recipient,
            subject=subject,
            body=self._build_lead_email_body(
                company=company,
                lead=lead,
                frontend_base_url=self._frontend_base_url,
            ),
        )
        await self._provider.send_email(message)
        self._lead_repository.mark_notification_sent(lead.id)
        logger.info("Sent lead notification for lead %s to %s", lead.id, recipient)
        return True

    async def send_lead_created(
        self,
        company: Company,
        lead: Lead,
        *,
        channel: ConversationChannel = ConversationChannel.WEB,
    ) -> bool:
        return await self.maybe_notify_lead(company, lead, channel=channel)

    @staticmethod
    def _build_lead_email_body(
        *,
        company: Company,
        lead: Lead,
        frontend_base_url: str | None = None,
    ) -> str:
        lines = [
            f"A new lead was captured for {company.name}.",
            "",
            f"Summary: {lead.summary or '—'}",
            f"Qualification status: {lead.qualification_status}",
            f"Lead score: {lead.lead_score}",
            f"Contact method: {lead.contact_method or 'unknown'}",
            f"Contactable: {'yes' if lead.contactable else 'no'}",
            "",
            f"Name: {lead.name}",
            f"Phone: {lead.phone}",
            f"Email: {lead.email or '—'}",
            f"Location: {lead.location}",
            f"Service requested: {lead.service_requested}",
            f"Urgency: {lead.urgency}",
            f"Preferred callback: {lead.preferred_callback_time}",
            f"Description: {lead.description}",
        ]
        if frontend_base_url:
            dashboard_url = f"{frontend_base_url.rstrip('/')}/leads/{lead.id}"
            lines.extend(["", f"View in dashboard: {dashboard_url}"])
        return "\n".join(lines)
