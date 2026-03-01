from dotenv import load_dotenv

load_dotenv()

from app.db.engine import SessionLocal
from app.models.user import User
from app.models.article import Article
from app.core.security import hash_password


def create_user(db, email: str, password: str, role: str) -> User:
    # Return existing user if already created
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing

    user = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)

    # Flush to get user.id without committing transaction
    db.flush()
    db.refresh(user)

    return user


def create_article(db, title: str, content: str, owner_id: int) -> None:
    # Simple article creation
    article = Article(
        title=title,
        content=content,
        owner_id=owner_id,
    )
    db.add(article)


if __name__ == "__main__":
    db = SessionLocal()

    admin = create_user(db, "admin@example.com", "admin123", "admin")
    admin1 = create_user(db, "admin1@example.com", "admin123", "admin")
    admin2 = create_user(db, "admin2@example.com", "admin123", "admin")

    editor = create_user(db, "editor@example.com", "editor123", "editor")
    editor2 = create_user(db, "editor2@example.com", "editor123", "editor")

    user = create_user(db, "user@example.com", "user123", "user")
    user2 = create_user(db, "user2@example.com", "user123", "user")

    # Seed some sample articles for different owners
    create_article(db, "Admin article", "Created by admin", admin.id)
    create_article(db, "Admin1 article", "Created by admin1", admin1.id)
    create_article(db, "Admin2 article", "Created by admin2", admin2.id)

    create_article(db, "Editor article", "Created by editor", editor.id)
    create_article(db, "Editor2 article", "Created by editor2", editor2.id)

    create_article(db, "User article", "Created by user", user.id)
    create_article(db, "User2 article", "Created by user2", user2.id)

    db.commit()
    db.close()

    print("Seed users + articles created")