from app.agents.lead_agent.utils import load_lead_data_from_context
from app.agents.lead_agent.models import LeadExtractedData
from app.core.llm.models import ChatMessage
from app.db.models.enums import MessageRole
from app.db.models.message import Message

LEAD_DATA_METADATA_KEY = "lead_data"


def load_lead_data_from_messages(messages: list[Message]) -> LeadExtractedData:
    for message in reversed(messages):
        metadata = message.message_metadata
        if isinstance(metadata, dict) and LEAD_DATA_METADATA_KEY in metadata:
            return load_lead_data_from_context(metadata[LEAD_DATA_METADATA_KEY])
    return LeadExtractedData()


def build_chat_messages(messages: list[Message], system_prompt: str) -> list[ChatMessage]:
    chat_messages = [ChatMessage(role="system", content=system_prompt)]
    for message in messages:
        if message.role in {MessageRole.USER.value, MessageRole.ASSISTANT.value}:
            chat_messages.append(ChatMessage(role=message.role, content=message.content))
    return chat_messages
