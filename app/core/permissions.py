from fastapi import HTTPException, status

from app.core.roles import ROLE_ADMIN, ROLE_EDITOR


def can_update_article(current_user, article) -> bool:
    # Owner can update own article
    if article.owner_id == current_user.id:
        return True

    # Editor and admin can update any article
    if current_user.role in (ROLE_EDITOR, ROLE_ADMIN):
        return True

    return False


def can_delete_article(current_user, article) -> bool:
    # Owner can delete own article
    if article.owner_id == current_user.id:
        return True

    # Only admin can delete any article
    if current_user.role == ROLE_ADMIN:
        return True

    return False


def require_admin(current_user) -> None:
    # Restrict access to admin-only endpoints
    if current_user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )