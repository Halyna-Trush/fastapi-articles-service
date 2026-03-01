from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.roles import ROLE_ADMIN, ROLE_EDITOR, ROLE_USER, is_admin
from app.db.deps import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserRoleUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def count_admins(db: Session) -> int:
    # Counts how many users currently have admin role
    return db.query(User).filter(User.role == ROLE_ADMIN).count()


@router.get(
    "/",
    response_model=List[UserRead],
    summary="List users (admin only)",
    description="Returns a paginated list of users. Supports optional search by email.",
    responses={
        401: {"description": "Unauthorized (missing or invalid token)"},
        403: {"description": "Forbidden (admin only)"},
    },
)
def list_users(
    search: Optional[str] = Query(
        default=None,
        description="Search users by email (case-insensitive).",
        examples={
            "search_example": {
                "summary": "Search by email",
                "value": "admin",
            }
        },
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of users returned.",
        examples={
            "default_limit": {
                "summary": "Default limit",
                "value": 10,
            }
        },
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of users to skip before returning results.",
        examples={
            "start": {
                "summary": "Start from beginning",
                "value": 0,
            }
        },
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Allow only admin to access users list
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    query = db.query(User).order_by(User.id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(User.email.ilike(pattern))

    return query.offset(offset).limit(limit).all()


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user by id (admin only)",
    description="Returns a single user by id.",
    responses={
        401: {"description": "Unauthorized (missing or invalid token)"},
        403: {"description": "Forbidden (admin only)"},
        404: {"description": "User not found"},
    },
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Allow only admin to access users
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.patch(
    "/{user_id}/role",
    response_model=UserRead,
    summary="Update user role (admin only)",
    description="Updates role for a user. Allowed roles: user, editor, admin.",
    responses={
        400: {"description": "Invalid role"},
        401: {"description": "Unauthorized (missing or invalid token)"},
        403: {"description": "Forbidden (admin only)"},
        404: {"description": "User not found"},
        409: {"description": "Cannot downgrade the last admin"},
    },
)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Allow only admin to update roles
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    if payload.role not in (ROLE_USER, ROLE_EDITOR, ROLE_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent removing admin access from the system
    # If this user is the last admin, it cannot be downgraded
    if user.role == ROLE_ADMIN and payload.role != ROLE_ADMIN:
        if count_admins(db) == 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot downgrade the last admin",
            )

    user.role = payload.role
    db.commit()
    db.refresh(user)

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (admin only)",
    description=(
        "Deletes a user by id.\n\n"
        "Notes:\n"
        "- Admin cannot delete itself\n"
        "- Last admin cannot be deleted\n"
        "- If user has related records, deletion is blocked"
    ),
    responses={
        400: {"description": "Admin cannot delete itself"},
        401: {"description": "Unauthorized (missing or invalid token)"},
        403: {"description": "Forbidden (admin only)"},
        404: {"description": "User not found"},
        409: {"description": "User has related records or last admin protection"},
    },
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Allow only admin to delete users
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Do not allow admin to delete itself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot delete itself",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent deleting the last admin
    if user.role == ROLE_ADMIN and count_admins(db) == 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete the last admin",
        )

    db.delete(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User cannot be deleted because it has related records",
        )

    return None