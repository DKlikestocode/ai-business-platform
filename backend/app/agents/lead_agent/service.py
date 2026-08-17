import logging
from uuid import UUID

from app.agents.lead_agent.appointment import sanitize_appointment_confirmation_preference
from app.agents.lead_agent.company_context import (
    build_business_contact_prompt,
    build_service_area_prompt,
    build_service_area_status_prompt,
)
from app.agents.lead_agent.conversation_history import (
    LEAD_DATA_METADATA_KEY,
    build_chat_messages,
    load_lead_data_from_messages,
)
from app.agents.lead_agent.contact_validation import (
    build_invalid_contact_reply,
    is_valid_phone,
    sanitize_contact_fields,
)
from app.agents.lead_agent.conversation_flow import resolve_qualification_reply
from app.agents.lead_agent.extraction import LeadExtractionClient
from app.agents.lead_agent.inquiry_scope import is_inquiry_out_of_scope
from app.agents.lead_agent.models import (
    LeadCaptureResult,
    LeadExtractedData,
    LeadMessageRequest,
    LeadMessageResponse,
    QualificationStatus,
)
from app.agents.lead_agent.qualification import (
    build_qualification_hint,
    evaluate_qualification,
)
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.urgency import sanitize_urgency_fields
from app.agents.lead_agent.utils import (
    build_message_response,
    get_missing_fields,
    is_lead_complete,
    merge_lead_data,
    serialize_lead_data,
)
from app.core.agent_engine.context import AgentContext
from app.core.llm.models import ChatMessage
from app.db.models.enums import ConversationChannel, MessageRole
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.intake_repository import IntakeRepository
from app.services.notifications.service import NotificationService
from app.services.service_area.evaluate import (
    evaluate_service_area,
    is_service_area_configured,
    resolve_lead_postal_code,
)
from app.services.service_area.models import ServiceAreaStatus
from app.trades.registry import build_trade_prompt

logger = logging.getLogger(__name__)


class LeadCaptureService:
    """Orchestrates lead capture conversations and persistence."""

    def __init__(
        self,
        *,
        agent: LeadCaptureAgent,
        conversation_repository: ConversationRepository,
        extraction_client: LeadExtractionClient,
        repository: LeadRepository,
        company_repository: CompanyRepository,
        activation_repository: CompanyActivationRepository,
        notification_service: NotificationService,
        channel: ConversationChannel = ConversationChannel.WEB,
        intake_repository: IntakeRepository | None = None,
    ) -> None:
        self._agent = agent
        self._conversation_repository = conversation_repository
        self._extraction_client = extraction_client
        self._repository = repository
        self._company_repository = company_repository
        self._activation_repository = activation_repository
        self._notification_service = notification_service
        self._channel = channel
        self._intake_repository = intake_repository

    async def handle_message(
        self,
        request: LeadMessageRequest,
        *,
        company_id: UUID,
        caller_phone: str | None = None,
    ) -> LeadMessageResponse:
        result = await self._process_message(
            request,
            company_id=company_id,
            caller_phone=caller_phone,
        )
        return build_message_response(result)

    async def _process_message(
        self,
        request: LeadMessageRequest,
        *,
        company_id: UUID,
        caller_phone: str | None = None,
    ) -> LeadCaptureResult:
        conversation = self._conversation_repository.get_or_create_by_external_id(
            company_id=company_id,
            external_id=request.conversation_id,
            channel=self._channel,
        )
        existing_messages = self._conversation_repository.list_messages(conversation.id)
        existing_data = load_lead_data_from_messages(existing_messages)
        if (
            caller_phone
            and self._channel == ConversationChannel.VOICE
            and not is_valid_phone(existing_data.phone)
        ):
            caller_data, _ = sanitize_contact_fields(LeadExtractedData(phone=caller_phone))
            existing_data, _ = sanitize_contact_fields(
                merge_lead_data(existing_data, caller_data),
            )
        pre_qualification = evaluate_qualification(existing_data, channel=self._channel)

        company = self._company_repository.get_by_id(company_id)
        company_trade = company.trade if company is not None else None
        service_area_prompt = (
            build_service_area_prompt(company) if company is not None else None
        )
        pre_service_area_eval = evaluate_service_area(company, existing_data)
        service_area_status_prompt = build_service_area_status_prompt(
            pre_service_area_eval,
            company=company,
        )
        trade_prompt = build_trade_prompt(company_trade) if company is not None else None
        business_contact_prompt = (
            build_business_contact_prompt(company) if company is not None else None
        )

        self._conversation_repository.add_message(
            conversation.id,
            MessageRole.USER,
            request.message,
        )

        agent_context = AgentContext(
            conversation_id=request.conversation_id,
            agent_name=self._agent.name,
            metadata={
                "known_lead_data": serialize_lead_data(existing_data),
                "qualification_hint": build_qualification_hint(
                    existing_data,
                    pre_qualification,
                    channel=self._channel,
                    service_area_configured=is_service_area_configured(company),
                ),
                "service_area_prompt": service_area_prompt,
                "service_area_status_prompt": service_area_status_prompt,
                "channel_voice_prompt": self._channel == ConversationChannel.VOICE,
                "trade_prompt": trade_prompt,
                "business_contact_prompt": business_contact_prompt,
            },
        )
        system_prompt = await self._agent.build_system_prompt(agent_context)
        history_messages = build_chat_messages(existing_messages, system_prompt)

        extraction_messages = [
            ChatMessage(
                role="system",
                content=(
                    f"{system_prompt}\n\n"
                    "Return a structured response with a conversational reply, inquiry_kind, "
                    "inquiry_scope (when trade context applies), and any lead fields "
                    "mentioned in the conversation."
                ),
            ),
            *history_messages[1:],
            ChatMessage(role="user", content=request.message),
        ]
        llm_output = await self._extraction_client.extract(messages=extraction_messages)
        incoming_data, rejected_contacts = sanitize_contact_fields(
            llm_output.to_extracted_data(),
        )
        merged_data, _ = sanitize_contact_fields(
            merge_lead_data(existing_data, incoming_data),
        )
        merged_data = sanitize_urgency_fields(merged_data)
        merged_data = sanitize_appointment_confirmation_preference(merged_data)
        if merged_data.postal_code is None:
            resolved_plz = resolve_lead_postal_code(merged_data)
            if resolved_plz is not None:
                merged_data = merged_data.model_copy(update={"postal_code": resolved_plz})

        service_area_eval = evaluate_service_area(company, merged_data)
        qualification = evaluate_qualification(merged_data, channel=self._channel)
        missing_fields = get_missing_fields(merged_data)
        lead_complete = is_lead_complete(merged_data)
        out_of_scope = is_inquiry_out_of_scope(
            llm_output.inquiry_scope,
            trade=company_trade,
        )
        reply = llm_output.reply
        if rejected_contacts.any_rejected:
            reply = build_invalid_contact_reply(rejected_contacts)
        elif not out_of_scope:
            reply = resolve_qualification_reply(
                merged_data=merged_data,
                channel=self._channel,
                llm_reply=reply,
                service_area_configured=is_service_area_configured(company),
            )

        self._conversation_repository.add_message(
            conversation.id,
            MessageRole.ASSISTANT,
            reply,
            metadata={
                LEAD_DATA_METADATA_KEY: merged_data.model_dump(mode="json"),
                "qualification_status": qualification.qualification_status.value,
                "lead_score": qualification.lead_score,
                "inquiry_scope": llm_output.inquiry_scope,
            },
        )

        lead_id: str | None = None
        summary = llm_output.summary
        if (
            not out_of_scope
            and qualification.should_persist
            and self._channel != ConversationChannel.LANDING_DEMO
        ):
            existing_lead = self._repository.get_by_conversation(
                request.conversation_id,
                company_id=company_id,
            )
            lead, _created = self._repository.save_or_update(
                company_id=company_id,
                conversation_id=request.conversation_id,
                data=merged_data,
                summary=summary,
                qualification=qualification,
                existing=existing_lead,
                service_area=service_area_eval,
            )
            lead_id = str(lead.id)
            logger.info(
                "Persisted lead %s for conversation %s (%s)",
                lead_id,
                request.conversation_id,
                qualification.qualification_status.value,
            )
            if self._intake_repository is not None:
                self._intake_repository.sync_lead(
                    lead,
                    conversation_channel=self._channel,
                )
            if self._channel == ConversationChannel.WEB:
                self._activation_repository.record_first_website_inquiry(
                    company_id,
                    lead_id=lead.id,
                    inquired_at=lead.created_at,
                )

            company = self._company_repository.get_by_id(company_id)
            if company is not None:
                became_qualified = (
                    pre_qualification.qualification_status != QualificationStatus.QUALIFIED
                    and qualification.qualification_status == QualificationStatus.QUALIFIED
                )
                await self._notification_service.maybe_notify_lead(
                    company,
                    lead,
                    channel=self._channel,
                )
                if became_qualified:
                    await self._notification_service.maybe_send_customer_confirmation(
                        company,
                        lead,
                    )

        return LeadCaptureResult(
            reply=reply,
            lead_complete=lead_complete,
            missing_fields=missing_fields,
            extracted_data=merged_data,
            lead_id=lead_id,
            summary=summary,
            contactable=qualification.contactable,
            contact_method=qualification.contact_method,
            lead_score=qualification.lead_score,
            qualification_status=qualification.qualification_status,
        )
