import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.api.router import api_router
from app.config import Settings, get_settings, validate_production_settings
from app.core.di.container import get_runtime_container
from app.middleware.public_widget_cors import PublicWidgetCORSMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    validate_production_settings(settings)

    logging.basicConfig(level=settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting %s (%s)", settings.app_name, settings.environment)

        container = get_runtime_container()
        container.register_agent(LeadCaptureAgent())

        yield
        logger.info("Shutting down %s", settings.app_name)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        PublicWidgetCORSMiddleware,
        public_path_prefix=f"{settings.api_prefix}/public/",
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.is_dir():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/health", tags=["health"], summary="Root liveness probe")
    def root_health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
