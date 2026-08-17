import asyncio
import logging
import signal

from app.config import get_settings, validate_production_settings
from app.db.session import SessionLocal
from app.repositories.intake_repository import IntakeRepository
from app.services.intake.extraction import OpenAIIntakeExtractionClient
from app.services.intake.service import IntakeService

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    settings = get_settings()
    validate_production_settings(settings)
    logging.basicConfig(level=settings.log_level)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signal_name in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signal_name, stop_event.set)

    if not settings.intake_email_enabled:
        logger.info("Inbound email intake is disabled; worker is idle")
        await stop_event.wait()
        return

    extraction_client = OpenAIIntakeExtractionClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url,
        organization=settings.openai_organization,
        timeout=settings.openai_timeout,
    )
    logger.info("Intake worker started")

    while not stop_event.is_set():
        processed = False
        session = SessionLocal()
        try:
            service = IntakeService(
                IntakeRepository(session),
                extraction_client=extraction_client,
            )
            processed = await service.process_next(
                max_attempts=settings.intake_max_processing_attempts,
                lease_seconds=settings.intake_worker_lease_seconds,
            )
        except Exception:
            session.rollback()
            logger.exception("Unexpected intake worker error")
        finally:
            session.close()

        if processed:
            continue
        try:
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=settings.intake_worker_poll_seconds,
            )
        except TimeoutError:
            pass

    logger.info("Intake worker stopped")


if __name__ == "__main__":
    asyncio.run(run_worker())
