from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api import auth
from api.main import app
from api.db import Base
from api.models import PaidSession, User, utcnow
from pdf.harvard import convert_markdown_to_harvard_pdf
from services.ats import compute_local_ats
from services.optimizer import build_optimize_prompts


class DummyRequest:
    def __init__(self, headers=None, cookies=None):
        self.headers = headers or {}
        self.cookies = cookies or {}


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_local_ats_shape():
    data = compute_local_ats("Python developer with a Computer Science degree", "Python developer role")
    assert set(data) == {
        "overall_score",
        "cosine_similarity",
        "keywords_present",
        "keywords_missing",
        "section_scores",
    }
    assert set(data["section_scores"]) == {"requirements", "experience", "terms", "education"}


def test_optimizer_prompt_rules_are_preserved():
    sys_prompt, user_prompt = build_optimize_prompts(
        "Original CV",
        "Python job",
        {"overall_score": 50, "keywords_missing": ["python"], "next_steps": []},
        {"q1": "N/A", "q2": "N/A", "q3": "N/A"},
    )
    assert "NEVER invent employers, dates, degrees, certifications, or tools" in sys_prompt
    assert "Output ONLY clean Markdown starting with '# Full Name'" in sys_prompt
    assert "Original resume:\nOriginal CV" in user_prompt


def test_owner_token_validation(monkeypatch):
    monkeypatch.setattr(auth.config, "OWNER_TOKEN", "secret")
    actor = auth.resolve_actor(DummyRequest(headers={"Authorization": "Bearer secret"}), make_db())
    assert actor.tier == "owner"


def test_paid_token_validation_and_credit_consumption():
    db = make_db()
    token = "paid-token"
    user = User(email="paid@example.com", credits_remaining=1)
    db.add(user)
    db.commit()
    paid_session = PaidSession(
        user_id=user.id,
        token_hash=auth.hash_token(token),
        expires_at=utcnow() + timedelta(days=1),
    )
    db.add(paid_session)
    db.commit()

    actor = auth.resolve_actor(DummyRequest(headers={"Authorization": f"Bearer {token}"}), db)
    assert actor.tier == "paid"
    assert auth.consume_paid_credit(db, actor) == 0


def test_pdf_generation_returns_pdf_bytes():
    pdf = convert_markdown_to_harvard_pdf("# Full Name\nemail@example.com\n## SKILLS\n- Python")
    assert pdf.startswith(b"%PDF")


def test_login_returns_session_without_granting_credits():
    client = TestClient(app)
    response = client.post("/api/auth/login", json={"email": "user@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["session_token"]
    assert data["credits_remaining"] == 0


def test_ats_score_is_available_without_auth():
    client = TestClient(app)
    response = client.post(
        "/api/ats-score",
        json={
            "cv": "Python developer with a Computer Science degree",
            "job": "Python developer role",
            "context": {"q1": "N/A", "q2": "N/A", "q3": "N/A"},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "Preview gratuito" in data["diagnostic"]
