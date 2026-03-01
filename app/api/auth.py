from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict, Field

from app.core.security import verify_password
from app.core.jwt import create_access_token
from app.db.deps import get_db
from app.db.users import get_user_by_email


class LoginRequest(BaseModel):
    """
    Login payload used to authenticate user.
    """

    email: str = Field(
        ...,
        description="User email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        description="User password",
        json_schema_extra={"format": "password"},
        examples=["strong_password"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "strong_password",
            }
        }
    )


class TokenResponse(BaseModel):
    """
    JWT token returned after successful authentication.
    """

    access_token: str = Field(
        ...,
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Token type for Authorization header",
        examples=["bearer"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description=(
        "Authenticate user with email and password and return a JWT access token. "
        "Use the token as: `Authorization: Bearer <token>`."
    ),
    responses={
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid credentials"}
                }
            },
        }
    },
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Validates credentials and returns a JWT token on success.
    """

    user = get_user_by_email(db, payload.email)

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role,
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )