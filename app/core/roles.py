# User roles used across the application
ROLE_USER = "user"
ROLE_EDITOR = "editor"
ROLE_ADMIN = "admin"

def is_admin(user) -> bool:
    # Check if current user has admin role
    return getattr(user, "role", None) == ROLE_ADMIN


def is_editor(user) -> bool:
    # Check if current user has editor role
    return getattr(user, "role", None) == ROLE_EDITOR