import logging

from datetime import datetime

from app.agents.lead_agent.contact_validation import is_valid_email, is_valid_phone
from app.agents.lead_agent.urgency import meets_notification_min_urgency
from app.agents.lead_agent.models import QualificationStatus
from app.agents.lead_agent.repository import LeadRepository
from app.db.models.company import Company
from app.db.models.enums import ConversationChannel
from app.db.models.lead import Lead
from app.services.notifications.interface import EmailMessage, EmailProvider
from app.services.notifications.lead_email_template import build_owner_lead_notification
from app.services.notifications.recipient import resolve_notification_recipient
from app.services.notifications.sms_interface import SmsMessage, SmsProvider

logger = logging.getLogger(__name__)


class NotificationService:
    """Coordinates outbound lead notifications."""

    def __init__(
        self,
        provider: EmailProvider,
        lead_repository: LeadRepository,
        *,
        sms_provider: SmsProvider | None = None,
        frontend_base_url: str | None = None,
    ) -> None:
        self._provider = provider
        self._lead_repository = lead_repository
        self._sms_provider = sms_provider
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

        if channel == ConversationChannel.WEB:
            if lead.qualification_status != QualificationStatus.QUALIFIED.value:
                return False
        else:
            contactable_allowed = lead.contactable or channel == ConversationChannel.WHATSAPP
            if not contactable_allowed:
                return False

        return meets_notification_min_urgency(
            lead.urgency,
            company.notification_min_urgency,
        )

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

        recipient = resolve_notification_recipient(company)
        if not recipient:
            logger.warning(
                "Skipping lead notification for company %s: no notification email configured.",
                company.id,
            )
            return False

        lead_name = lead.name or "Ohne Namen"
        subject = (
            f"Neue qualifizierte Anfrage: {lead_name}"
            if lead.qualification_status == QualificationStatus.QUALIFIED.value
            else f"Neue kontaktierbare Anfrage: {lead_name}"
        )
        plain_body, html_body = build_owner_lead_notification(
            company=company,
            lead=lead,
            frontend_base_url=self._frontend_base_url,
        )
        message = EmailMessage(
            to=recipient,
            subject=subject,
            body=plain_body,
            html=html_body,
        )
        await self._provider.send_email(message)
        self._lead_repository.mark_notification_sent(lead.id)
        logger.info("Sent lead notification for lead %s to %s", lead.id, recipient)
        return True

    def should_send_customer_confirmation(
        self,
        company: Company,
        lead: Lead,
    ) -> bool:
        if not company.send_customer_confirmation:
            return False
        if lead.customer_confirmation_sent_at is not None:
            return False
        if lead.qualification_status != QualificationStatus.QUALIFIED.value:
            return False
        return is_valid_email(lead.email) or is_valid_phone(lead.phone)

    async def maybe_send_customer_confirmation(
        self,
        company: Company,
        lead: Lead,
    ) -> bool:
        if not self.should_send_customer_confirmation(company, lead):
            logger.info(
                "Skipping customer confirmation for lead %s (status=%s).",
                lead.id,
                lead.qualification_status,
            )
            return False

        sent_any = False
        if is_valid_email(lead.email):
            message = EmailMessage(
                to=lead.email,
                subject=f"Ihre Anfrage bei {company.name}",
                body=self._build_customer_confirmation_email_body(company=company, lead=lead),
            )
            await self._provider.send_email(message)
            sent_any = True
            logger.info("Sent customer confirmation email for lead %s to %s", lead.id, lead.email)

        if is_valid_phone(lead.phone) and self._sms_provider is not None:
            sms = SmsMessage(
                to=lead.phone,
                body=self._build_customer_confirmation_sms_body(company=company, lead=lead),
            )
            await self._sms_provider.send_sms(sms)
            sent_any = True
            logger.info("Sent customer confirmation SMS for lead %s to %s", lead.id, lead.phone)

        if sent_any:
            self._lead_repository.mark_customer_confirmation_sent(lead.id)
        return sent_any

    async def send_appointment_confirmation_email(
        self,
        company: Company,
        lead: Lead,
    ) -> datetime | None:
        if lead.appointment_confirmation_sent_at is not None:
            return lead.appointment_confirmation_sent_at
        if not is_valid_email(lead.email):
            return None

        message = EmailMessage(
            to=lead.email,
            subject=f"Terminbestätigung — {company.name}",
            body=self._build_appointment_confirmation_email_body(company=company, lead=lead),
        )
        await self._provider.send_email(message)
        marked = self._lead_repository.mark_appointment_confirmation_sent(lead.id)
        if marked is None:
            return None
        logger.info(
            "Sent appointment confirmation email for lead %s to %s",
            lead.id,
            lead.email,
        )
        return marked.appointment_confirmation_sent_at

    async def send_appointment_confirmation_sms(
        self,
        company: Company,
        lead: Lead,
    ) -> bool:
        logger.info(
            "Appointment confirmation SMS not implemented for lead %s (company %s).",
            lead.id,
            company.id,
        )
        return False

    async def send_lead_created(
        self,
        company: Company,
        lead: Lead,
        *,
        channel: ConversationChannel = ConversationChannel.WEB,
    ) -> bool:
        return await self.maybe_notify_lead(company, lead, channel=channel)

    async def send_test_inquiry_notification(self, company: Company) -> None:
        recipient = resolve_notification_recipient(company)
        if not recipient:
            raise ValueError("No notification email configured.")

        subject = "Test: Neue Anfrage über Ihren Website-Chat"
        body = self._build_test_inquiry_email_body(company=company)
        message = EmailMessage(to=recipient, subject=subject, body=body)
        await self._provider.send_email(message)
        logger.info(
            "Sent test inquiry notification for company %s to %s",
            company.id,
            recipient,
        )

    async def send_password_reset_email(self, *, to: str, reset_url: str) -> None:
        subject = "Passwort zurücksetzen — AI Anfragen-Assistent"
        body = "\n".join(
            [
                "Sie haben ein neues Passwort für Ihr AI Anfragen-Assistent-Konto angefordert.",
                "",
                "Öffnen Sie den folgenden Link, um ein neues Passwort zu setzen:",
                reset_url,
                "",
                "Der Link ist 60 Minuten gültig. Wenn Sie diese Anfrage nicht gestellt haben,",
                "können Sie diese E-Mail ignorieren.",
            ],
        )
        message = EmailMessage(to=to, subject=subject, body=body)
        await self._provider.send_email(message)
        logger.info("Sent password reset email to %s", to)

    @staticmethod
    def _build_test_inquiry_email_body(*, company: Company) -> str:
        return "\n".join(
            [
                "Dies ist eine Test-E-Mail vom AI Anfragen-Assistenten.",
                "",
                f"Sie erhalten diese Nachricht, weil Sie einen Test für {company.name} "
                "ausgelöst haben.",
                "",
                "Ihre E-Mail-Benachrichtigungen funktionieren. Bei echten Website-Anfragen "
                "erhalten Sie eine ähnliche Nachricht mit den Details der Anfrage.",
                "",
                "—",
                "Beispiel einer echten Anfrage (nur zur Veranschaulichung):",
                "",
                "Zusammenfassung: Undichtigkeit in der Küche — dringend",
                "Name: Sabine Wagner",
                "Telefon: +49 170 1234567",
                "E-Mail: sabine@example.com",
                "Angefragter Service: Rohrreparatur",
                "Dringlichkeit: Hoch",
            ],
        )

    @staticmethod
    def _build_customer_confirmation_email_body(*, company: Company, lead: Lead) -> str:
        if lead.name and lead.name.strip():
            greeting = f"Guten Tag {lead.name.strip()},"
        else:
            greeting = "Guten Tag,"

        lines = [
            greeting,
            "",
            f"vielen Dank für Ihre Anfrage bei {company.name}.",
            "Wir haben alle Angaben erhalten und melden uns in Kürze bei Ihnen.",
            "",
            f"Zusammenfassung: {lead.summary or lead.description or lead.service_requested or 'Ihr Anliegen'}",
        ]
        if lead.preferred_callback_time:
            lines.append(f"Terminwunsch: {lead.preferred_callback_time}")
        if company.phone:
            lines.append(f"Telefon: {company.phone}")
        if company.email:
            lines.append(f"E-Mail: {company.email}")
        lines.extend(
            [
                "",
                "Mit freundlichen Grüßen",
                company.name,
            ],
        )
        return "\n".join(lines)

    @staticmethod
    def _build_customer_confirmation_sms_body(*, company: Company, lead: Lead) -> str:
        summary = lead.summary or lead.description or lead.service_requested or "Ihr Anliegen"
        return (
            f"{company.name}: Vielen Dank für Ihre Anfrage. "
            f"Wir haben alles erhalten ({summary}) und melden uns in Kürze."
        )

    @staticmethod
    def _build_appointment_confirmation_email_body(*, company: Company, lead: Lead) -> str:
        if lead.name and lead.name.strip():
            greeting = f"Guten Tag {lead.name.strip()},"
        else:
            greeting = "Guten Tag,"

        lines = [
            greeting,
            "",
            f"vielen Dank für Ihre Terminanfrage bei {company.name}.",
            "Wir haben Ihren Terminwunsch erhalten und melden uns zur Bestätigung.",
            "",
            f"Terminwunsch: {lead.preferred_callback_time or '—'}",
            f"Anliegen: {lead.summary or lead.description or lead.service_requested or '—'}",
        ]
        if company.phone:
            lines.append(f"Telefon: {company.phone}")
        if company.email:
            lines.append(f"E-Mail: {company.email}")
        lines.extend(
            [
                "",
                "Mit freundlichen Grüßen",
                company.name,
            ],
        )
        return "\n".join(lines)
