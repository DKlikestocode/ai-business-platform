from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.rate_limit import get_rate_limiter

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.openai_client import OpenAILeadExtractionClient
from app.agents.lead_agent.dashboard_service import LeadDashboardService
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.config import Settings, get_settings
from app.core.auth.jwt import decode_access_token
from app.core.di.container import RuntimeContainer, get_runtime_container
from app.db.models.user import User
from app.db.models.enums import ConversationChannel
from app.db.session import get_db
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.user_repository import UserRepository
from app.services.activation.service import ActivationService
from app.services.auth_service import AuthService
from app.services.notifications.factory import build_email_provider
from app.services.notifications.service import NotificationService
from app.services.tenant_service import CompanyService, UserService

bearer_scheme = HTTPBearer(auto_error=False)
_AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}


def require_development_environment(
    settings: Settings = Depends(get_settings),
) -> None:
    if not settings.is_development:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Self-service registration is disabled in production.",
        )


def require_registration_enabled(
    settings: Settings = Depends(get_settings),
) -> None:
    if settings.is_development or settings.self_serve_registration_enabled:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Self-service registration is disabled in production.",
    )


class RateLimit:
    def __init__(self, *, limit: int, window_seconds: int, scope: str) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.scope = scope

    def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{self.scope}:{client_ip}"
        if not get_rate_limiter().allow(key, self.limit, self.window_seconds):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )


def get_runtime() -> RuntimeContainer:
    return get_runtime_container()


def get_notification_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> NotificationService:
    return NotificationService(
        provider=build_email_provider(settings),
        lead_repository=LeadRepository(db),
        frontend_base_url=settings.frontend_base_url,
    )


def get_lead_capture_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    notification_service: NotificationService = Depends(get_notification_service),
) -> LeadCaptureService:
    return _build_lead_capture_service(
        db=db,
        settings=settings,
        notification_service=notification_service,
        channel=ConversationChannel.DASHBOARD,
    )


def get_widget_lead_capture_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    notification_service: NotificationService = Depends(get_notification_service),
) -> LeadCaptureService:
    return _build_lead_capture_service(
        db=db,
        settings=settings,
        notification_service=notification_service,
        channel=ConversationChannel.WEB,
    )


def get_voice_lead_capture_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    notification_service: NotificationService = Depends(get_notification_service),
) -> LeadCaptureService:
    return _build_lead_capture_service(
        db=db,
        settings=settings,
        notification_service=notification_service,
        channel=ConversationChannel.VOICE,
    )


def get_landing_demo_lead_capture_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    notification_service: NotificationService = Depends(get_notification_service),
) -> LeadCaptureService:
    return _build_lead_capture_service(
        db=db,
        settings=settings,
        notification_service=notification_service,
        channel=ConversationChannel.LANDING_DEMO,
    )


def _build_lead_capture_service(
    *,
    db: Session,
    settings: Settings,
    notification_service: NotificationService,
    channel: ConversationChannel,
) -> LeadCaptureService:
    return LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db),
        extraction_client=OpenAILeadExtractionClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url,
            organization=settings.openai_organization,
            timeout=settings.openai_timeout,
        ),
        repository=LeadRepository(db),
        company_repository=CompanyRepository(db),
        activation_repository=CompanyActivationRepository(db),
        notification_service=notification_service,
        channel=channel,
    )


def get_lead_repository(db: Session = Depends(get_db)) -> LeadRepository:
    return LeadRepository(db)


def get_conversation_repository(db: Session = Depends(get_db)) -> ConversationRepository:
    return ConversationRepository(db)


def get_lead_dashboard_service(
    repository: LeadRepository = Depends(get_lead_repository),
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
    db: Session = Depends(get_db),
) -> LeadDashboardService:
    return LeadDashboardService(
        repository,
        conversation_repository,
        CompanyActivationRepository(db),
    )


def get_company_repository(db: Session = Depends(get_db)) -> CompanyRepository:
    return CompanyRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_company_activation_repository(
    db: Session = Depends(get_db),
) -> CompanyActivationRepository:
    return CompanyActivationRepository(db)


def get_activation_service(
    company_repository: CompanyRepository = Depends(get_company_repository),
    activation_repository: CompanyActivationRepository = Depends(
        get_company_activation_repository,
    ),
    settings: Settings = Depends(get_settings),
) -> ActivationService:
    return ActivationService(
        company_repository,
        activation_repository,
        public_api_base_url=settings.public_api_base_url,
        frontend_base_url=settings.frontend_base_url,
        cors_origins=settings.cors_origins_list,
        widget_stale_after_hours=settings.widget_stale_after_hours,
    )


def get_company_service(
    repository: CompanyRepository = Depends(get_company_repository),
) -> CompanyService:
    return CompanyService(repository)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    company_repository: CompanyRepository = Depends(get_company_repository),
) -> UserService:
    return UserService(user_repository, company_repository)


def get_password_reset_repository(
    db: Session = Depends(get_db),
) -> PasswordResetRepository:
    return PasswordResetRepository(db)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    password_reset_repository: PasswordResetRepository = Depends(get_password_reset_repository),
    notification_service: NotificationService = Depends(get_notification_service),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(
        user_repository,
        settings,
        password_reset_repository=password_reset_repository,
        notification_service=notification_service,
    )


def _resolve_user_from_credentials(
    credentials: HTTPAuthorizationCredentials | None,
    *,
    user_repository: UserRepository,
    settings: Settings,
) -> User | None:
    if credentials is None:
        return None

    try:
        user_id = decode_access_token(credentials.credentials, settings)
    except jwt.InvalidTokenError:
        return None

    user = user_repository.get_by_id(user_id)
    if user is None or not user.is_active:
        return None

    return user


def get_optional_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    user_repository: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> User | None:
    return _resolve_user_from_credentials(
        credentials,
        user_repository=user_repository,
        settings=settings,
    )


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    user_repository: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> User:
    user = _resolve_user_from_credentials(
        credentials,
        user_repository=user_repository,
        settings=settings,
    )
    if user is None:
        detail = "Not authenticated." if credentials is None else "Invalid access token."
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=_AUTH_HEADERS,
        )

    return user


def get_current_tenant_id(
    current_user: User = Depends(get_current_user),
) -> UUID:
    return current_user.company_id
