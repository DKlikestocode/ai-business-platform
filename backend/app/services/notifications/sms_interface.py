from dataclasses import dataclass


@dataclass(frozen=True)
class SmsMessage:
    to: str
    body: str


class SmsProvider:
    async def send_sms(self, message: SmsMessage) -> None:
        raise NotImplementedError
