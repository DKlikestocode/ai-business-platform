import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.agent import Agent
    from app.db.models.company_activation import CompanyActivation
    from app.db.models.conversation import Conversation
    from app.db.models.intake import IntakeItem
    from app.db.models.lead import Lead
    from app.db.models.user import User


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notification_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notification_min_urgency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
    )
    notify_on_new_lead: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notify_on_contactable_lead: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    contactable_lead_notification_threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=50,
    )
    service_area_center: Mapped[str | None] = mapped_column(String(255), nullable=True)
    service_radius_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    service_area_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    service_area_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    trade: Mapped[str | None] = mapped_column(String(32), nullable=True)
    send_customer_confirmation: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    chat_share_phone: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    chat_share_email: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    intake_items: Mapped[list["IntakeItem"]] = relationship(
        "IntakeItem",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    agents: Mapped[list["Agent"]] = relationship(
        "Agent",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    activation: Mapped["CompanyActivation | None"] = relationship(
        "CompanyActivation",
        back_populates="company",
        cascade="all, delete-orphan",
        uselist=False,
    )
