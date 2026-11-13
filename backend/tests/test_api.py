import sys
from pathlib import Path
import pytest

try:
    import faiss
except Exception:
    pass

from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.main import app
from app.config import settings

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "Zyro Dynamics Pvt. Ltd."
    assert data["status"] == "operational"

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["index_loaded"] is True
    assert data["total_indexed_chunks"] == 91
    assert "llama" in data["model"].lower()

def test_valid_hr_question_earned_leave(client):
    response = client.post(
        "/chat",
        json={"question": "How does Earned Leave accrue every month?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 10
    assert "sources" in data
    assert len(data["sources"]) > 0
    # Citations must have real document names and page numbers
    assert any("Leave_Policy.pdf" in s["file"] for s in data["sources"])
    assert all("page" in s and s["page"] for s in data["sources"])

def test_valid_hr_question_salary(client):
    response = client.post(
        "/chat",
        json={"question": "When is monthly salary credited?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["sources"]) > 0

def test_out_of_scope_geography(client):
    response = client.post(
        "/chat",
        json={"question": "What is the capital of France?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_refusal"] is True
    assert "Zyro Dynamics" in data["answer"]
    assert len(data["sources"]) == 0

def test_out_of_scope_google_ceo(client):
    response = client.post(
        "/chat",
        json={"question": "Who is the CEO of Google?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_refusal"] is True
    assert len(data["sources"]) == 0

def test_unsupported_wifi_password(client):
    response = client.post(
        "/chat",
        json={"question": "What is the company office WiFi password?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_refusal"] is True
    assert len(data["sources"]) == 0

def test_empty_question_validation(client):
    # Empty string should fail Pydantic min_length=2 validation
    response = client.post("/chat", json={"question": ""})
    assert response.status_code == 422

def test_whitespace_only_question_validation(client):
    response = client.post("/chat", json={"question": " "})
    assert response.status_code == 422

def test_excessively_long_question_validation(client):
    long_q = "How does leave work? " * 150  # Over 2000 characters
    response = client.post("/chat", json={"question": long_q})
    assert response.status_code == 422

def test_admin_reindex_unauthorized(client):
    response = client.post("/admin/reindex", json={"admin_key": "wrong_key"})
    assert response.status_code == 401

def test_admin_reindex_authorized(client):
    response = client.post(
        "/admin/reindex",
        json={"admin_key": settings.ADMIN_API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_chunks"] == 91

