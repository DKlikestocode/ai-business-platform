import logging

from app.agents.lead_agent.urgency import meets_notification_min_urgency
from app.agents.lead_agent.models import QualificationStatus
from app.agents.lead_agent.repository import LeadRepository
from app.db.models.company import Company
from app.db.models.enums import ConversationChannel
from app.db.models.lead import Lead
from app.services.notifications.interface import EmailMessage, EmailProvider
from app.services.notifications.recipient import resolve_notification_recipient

logger = logging.getLogger(__name__)

_QUALIFICATION_LABELS = {
    QualificationStatus.QUALIFIED.value: "Qualifiziert",
    QualificationStatus.CONTACTABLE.value: "Kontaktierbar",
    QualificationStatus.INCOMPLETE.value: "Unvollständig",
}

_CONTACT_METHOD_LABELS = {
    "phone": "Telefon",
    "email": "E-Mail",
    "channel": "Kanal",
    "unknown": "Unbekannt",
}


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
    def _qualification_label(status: str) -> str:
        return _QUALIFICATION_LABELS.get(status, status)

    @staticmethod
    def _contact_method_label(method: str | None) -> str:
        if not method:
            return _CONTACT_METHOD_LABELS["unknown"]
        return _CONTACT_METHOD_LABELS.get(method, method)

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
    def _build_lead_email_body(
        *,
        company: Company,
        lead: Lead,
        frontend_base_url: str | None = None,
    ) -> str:
        lines = [
            f"Es wurde eine neue Anfrage für {company.name} erfasst.",
            "",
            f"Zusammenfassung: {lead.summary or '—'}",
            (
                "Qualifizierungsstatus: "
                f"{NotificationService._qualification_label(lead.qualification_status)}"
            ),
            f"Priorität: {lead.lead_score}",
            (
                "Kontaktmethode: "
                f"{NotificationService._contact_method_label(lead.contact_method)}"
            ),
            f"Kontaktierbar: {'Ja' if lead.contactable else 'Nein'}",
            "",
            f"Name: {lead.name or '—'}",
            f"Telefon: {lead.phone or '—'}",
            f"E-Mail: {lead.email or '—'}",
            f"Standort: {lead.location or '—'}",
            f"Angefragter Service: {lead.service_requested or '—'}",
            f"Dringlichkeit: {lead.urgency or '—'}",
            f"Terminwunsch: {lead.preferred_callback_time or '—'}",
            f"Beschreibung: {lead.description or '—'}",
        ]
        if frontend_base_url:
            dashboard_url = f"{frontend_base_url.rstrip('/')}/leads/{lead.id}"
            lines.extend(["", f"Im Dashboard anzeigen: {dashboard_url}"])
        return "\n".join(lines)
