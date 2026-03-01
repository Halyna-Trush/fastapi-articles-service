from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_articles_unauthorized():
    response = client.get("/articles/")

    assert response.status_code in (401, 403)