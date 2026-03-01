from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.api.admin_users import router as admin_users_router
from app.api.articles import router as articles_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.db.session import get_connection

app = FastAPI(
    title="FastAPI Articles Service",
    version="0.1.0",
    description=(
        "A simple Articles CRUD service with JWT auth and role-based access control.\n\n"
        "Auth:\n"
        "- Use POST /auth/login to get a Bearer token\n"
        "- Click Authorize in /docs and paste the token\n\n"
        "Roles:\n"
        "- user: manage own articles, read others\n"
        "- editor: update any article, cannot delete others' articles (403)\n"
        "- admin: full access to users and articles\n"
    ),
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(articles_router)
app.include_router(admin_users_router)


def db_ok() -> bool:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return True
    finally:
        conn.close()


@app.get("/health")
def health_check():
    try:
        result = db_ok()
        print("DB CHECK RESULT:", result)
        return {
            "status": "ok",
            "db_ok": result,
        }
    except Exception as e:
        print("DB ERROR:", e)
        return {
            "status": "ok",
            "db_error": str(e),
        }
    
    