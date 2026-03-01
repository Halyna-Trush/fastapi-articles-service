from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user",
    description="Returns currently authenticated user. JWT Bearer token is required.",
)
def read_current_user(current_user=Depends(get_current_user)):
    return current_user