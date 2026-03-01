from fastapi.testclient import TestClient

from app.main import app
from app.db.engine import SessionLocal
from app.models.user import User
from app.core.security import hash_password

client = TestClient(app)


def _ensure_user(email: str, password: str, role: str) -> User:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            return user

        user = User(
            email=email,
            password_hash=hash_password(password),
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def _login(email: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_admin_cannot_delete_itself():
    admin_email = "admin_selfdelete@example.com"
    admin_password = "admin123"

    admin = _ensure_user(admin_email, admin_password, "admin")
    token = _login(admin_email, admin_password)

    response = client.delete(
        f"/users/{admin.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Admin cannot delete itself"


def test_admin_can_delete_other_admin_when_not_self():
    admin1_email = "admin_delete_1@example.com"
    admin2_email = "admin_delete_2@example.com"
    admin_password = "admin123"

    admin1 = _ensure_user(admin1_email, admin_password, "admin")
    admin2 = _ensure_user(admin2_email, admin_password, "admin")

    token = _login(admin1_email, admin_password)

    response = client.delete(
        f"/users/{admin2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204, response.text