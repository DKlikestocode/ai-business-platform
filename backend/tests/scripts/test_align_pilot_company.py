import uuid

from app.core.security import hash_password
from app.db.models.enums import UserRole
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository
from app.scripts.align_pilot_company import align_pilot_company


def test_align_pilot_company_renames_user_company_slug(db_session) -> None:
    suffix = uuid.uuid4().hex[:8]
    source_slug = f"align-source-{suffix}"
    target_slug = f"align-target-{suffix}"
    shell_slug = f"align-shell-{suffix}"
    owner_email = f"align-owner-{suffix}@example.com"

    company_repo = CompanyRepository(db_session)
    user_repo = UserRepository(db_session)

    company = company_repo.create(
        name="Mike's Sanitärdienst",
        email=owner_email,
        slug=source_slug,
    )
    user_repo.create(
        company_id=company.id,
        first_name="Dominik",
        last_name="Kessling",
        email=owner_email,
        password_hash=hash_password("password123"),
        role=UserRole.OWNER,
    )
    company_repo.create(
        name="Duplicate shell",
        email=f"shell-{suffix}@example.com",
        slug=shell_slug,
    )

    result_slug = align_pilot_company(
        user_email=owner_email,
        target_slug=target_slug,
        company_name="Dominik's Dienstleistungsbetrieb",
        public_email="hallo@dominiksdomain.com",
        session=db_session,
    )

    db_session.expire_all()
    assert result_slug == target_slug
    user = user_repo.get_by_email(owner_email)
    assert user is not None
    aligned = company_repo.get_by_id(user.company_id)
    assert aligned is not None
    assert aligned.slug == target_slug
    assert aligned.name == "Dominik's Dienstleistungsbetrieb"
    assert aligned.email == "hallo@dominiksdomain.com"
    assert company_repo.get_by_slug(source_slug) is None
