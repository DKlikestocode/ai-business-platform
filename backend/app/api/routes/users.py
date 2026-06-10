from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_user_service, require_development_environment
from app.api.schemas.users import UserCreateRequest, UserResponse, user_to_response
from app.domain.exceptions import ConflictError, NotFoundError
from app.services.tenant_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    dependencies=[Depends(require_development_environment)],
)
def create_user(
    payload: UserCreateRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        user = service.create_user(
            company_id=payload.company_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=str(payload.email),
            password=payload.password,
            role=payload.role,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return user_to_response(user)
