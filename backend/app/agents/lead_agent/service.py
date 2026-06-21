import logging
from uuid import UUID

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.conversation_history import (
    LEAD_DATA_METADATA_KEY,
    build_chat_messages,
    load_lead_data_from_messages,
)
from app.agents.lead_agent.extraction import LeadExtractionClient
from app.agents.lead_agent.models import (
    LeadCaptureResult,
    LeadMessageRequest,
    LeadMessageResponse,
)
from app.agents.lead_agent.qualification import (
    build_qualification_hint,
    evaluate_qualification,
)
from app.agents.lead_agent.repository import LeadRepository
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
from app.services.notifications.service import NotificationService

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
    ) -> None:
        self._agent = agent
        self._conversation_repository = conversation_repository
        self._extraction_client = extraction_client
        self._repository = repository
        self._company_repository = company_repository
        self._activation_repository = activation_repository
        self._notification_service = notification_service
        self._channel = channel

    async def handle_message(
        self,
        request: LeadMessageRequest,
        *,
        company_id: UUID,
    ) -> LeadMessageResponse:
        result = await self._process_message(request, company_id=company_id)
        return build_message_response(result)

    async def _process_message(
        self,
        request: LeadMessageRequest,
        *,
        company_id: UUID,
    ) -> LeadCaptureResult:
        conversation = self._conversation_repository.get_or_create_by_external_id(
            company_id=company_id,
            external_id=request.conversation_id,
            channel=self._channel,
        )
        existing_messages = self._conversation_repository.list_messages(conversation.id)
        existing_data = load_lead_data_from_messages(existing_messages)
        pre_qualification = evaluate_qualification(existing_data, channel=self._channel)

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
                ),
            },
        )
        system_prompt = await self._agent.build_system_prompt(agent_context)
        history_messages = build_chat_messages(existing_messages, system_prompt)

        extraction_messages = [
            ChatMessage(
                role="system",
                content=(
                    f"{system_prompt}\n\n"
                    "Return a structured response with a conversational reply and any "
                    "lead fields mentioned in the conversation."
                ),
            ),
            *history_messages[1:],
            ChatMessage(role="user", content=request.message),
        ]
        llm_output = await self._extraction_client.extract(messages=extraction_messages)
        merged_data = merge_lead_data(existing_data, llm_output.to_extracted_data())
        qualification = evaluate_qualification(merged_data, channel=self._channel)
        missing_fields = get_missing_fields(merged_data)
        lead_complete = is_lead_complete(merged_data)

        self._conversation_repository.add_message(
            conversation.id,
            MessageRole.ASSISTANT,
            llm_output.reply,
            metadata={
                LEAD_DATA_METADATA_KEY: merged_data.model_dump(mode="json"),
                "qualification_status": qualification.qualification_status.value,
                "lead_score": qualification.lead_score,
            },
        )

        lead_id: str | None = None
        summary = llm_output.summary
        if (
            qualification.should_persist
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
            )
            lead_id = str(lead.id)
            logger.info(
                "Persisted lead %s for conversation %s (%s)",
                lead_id,
                request.conversation_id,
                qualification.qualification_status.value,
            )
            if self._channel == ConversationChannel.WEB:
                self._activation_repository.record_first_website_inquiry(
                    company_id,
                    lead_id=lead.id,
                    inquired_at=lead.created_at,
                )

            company = self._company_repository.get_by_id(company_id)
            if company is not None:
                await self._notification_service.maybe_notify_lead(
                    company,
                    lead,
                    channel=self._channel,
                )

        return LeadCaptureResult(
            reply=llm_output.reply,
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
