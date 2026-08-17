from uuid import UUID

from pydantic import BaseModel


class ResendWebhookAcceptedResponse(BaseModel):
    accepted: bool
    created: bool
    intake_item_id: UUID
