"""Seed the database with demo leads for local development."""

from app.agents.lead_agent.repository import LeadRepository
from app.db.session import SessionLocal
from app.demo.seed import get_or_create_demo_company, seed_demo_leads
from app.repositories.company_repository import CompanyRepository


def main() -> None:
    session = SessionLocal()
    try:
        lead_repository = LeadRepository(session)
        company_repository = CompanyRepository(session)
        get_or_create_demo_company(company_repository)
        result = seed_demo_leads(
            lead_repository,
            company_repository=company_repository,
        )
        print(result.message)
        if result.lead_ids:
            print("Created lead IDs:")
            for lead_id in result.lead_ids:
                print(f"  - {lead_id}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
