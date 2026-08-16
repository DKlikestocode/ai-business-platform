from fastapi import APIRouter

from app.api.routes import (
    auth,
    companies,
    company_activation,
    company_settings,
    conversations,
    dev,
    health,
    intake,
    lead_agent,
    leads,
    public_voice,
    public_widget,
    public_site,
    landing_demo,
    users,
    webhooks,
)
from app.config import get_settings

settings = get_settings()

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(public_widget.router)
api_router.include_router(public_site.router)
api_router.include_router(public_voice.router)
api_router.include_router(webhooks.router)
api_router.include_router(landing_demo.router)
api_router.include_router(auth.router)
api_router.include_router(companies.router)
api_router.include_router(company_settings.router)
api_router.include_router(company_activation.router)
api_router.include_router(users.router)
api_router.include_router(lead_agent.router)
api_router.include_router(conversations.router)
api_router.include_router(leads.router)
api_router.include_router(intake.router)

if settings.is_development:
    api_router.include_router(dev.router)
