from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.agent import Agent


class AgentRepository:
    """Persistence layer for tenant agent registrations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        company_id: UUID,
        name: str,
        agent_type: str,
        is_active: bool = True,
    ) -> Agent:
        agent = Agent(
            company_id=company_id,
            name=name,
            agent_type=agent_type,
            is_active=is_active,
        )
        self._session.add(agent)
        self._session.commit()
        self._session.refresh(agent)
        return agent

    def get_by_type(self, *, company_id: UUID, agent_type: str) -> Agent | None:
        return (
            self._session.query(Agent)
            .filter(
                Agent.company_id == company_id,
                Agent.agent_type == agent_type,
            )
            .one_or_none()
        )
