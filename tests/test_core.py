from io import BytesIO
from types import SimpleNamespace
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from PyPDF2 import PdfReader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api import auth, billing
from api.db import get_db
from api.main import app
from api.db import Base
from api.models import CheckoutRecord, PaidSession, User, utcnow
from pdf.harvard import convert_markdown_to_harvard_pdf, split_pipe_line
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


def make_test_sessionmaker():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def client_and_db():
    SessionTesting = make_test_sessionmaker()
    db = SessionTesting()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app), db
    finally:
        app.dependency_overrides.clear()
        db.close()


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


def test_pdf_contact_fields_preserve_phone_email_and_address():
    pdf = convert_markdown_to_harvard_pdf(
        "# Full Name\n"
        "+351 916348286 | user@example.com | Lisboa, Portugal\n"
        "linkedin.com/in/example\n"
        "## SKILLS\n"
        "- Python"
    )
    text = PdfReader(BytesIO(pdf)).pages[0].extract_text()
    assert "+351 916348286" in text
    assert "user@example.com" in text
    assert "Lisboa, Portugal" in text


def test_pdf_contact_fields_normalize_phone_spacing_variants():
    pdf = convert_markdown_to_harvard_pdf(
        "# Full Name\n"
        "\uff0b351\u00a0916348286 | user@example.com | Lisboa\u202fPortugal\n"
        "## SKILLS\n"
        "- Python"
    )
    text = PdfReader(BytesIO(pdf)).pages[0].extract_text()
    assert "+351 916348286" in text
    assert "user@example.com" in text
    assert "Lisboa Portugal" in text


def test_pdf_long_contact_line_is_split_across_two_lines():
    contact = "+351 916348286 | user@example.com | Lisboa, Portugal | github.com/user | linkedin.com/in/user"

    assert split_pipe_line(contact) == [
        "+351 916348286 | user@example.com",
        "Lisboa, Portugal | github.com/user | linkedin.com/in/user",
    ]

    pdf = convert_markdown_to_harvard_pdf(
        "# Full Name\n"
        f"{contact}\n"
        "## SKILLS\n"
        "- Python"
    )
    text = PdfReader(BytesIO(pdf)).pages[0].extract_text()
    assert "+351 916348286 | user@example.com" in text
    assert "user@example.com\nLisboa, Portugal" in text
    assert "github.com/user" in text
    assert "linkedin.com/in/user" in text


def test_login_returns_session_without_granting_credits(client_and_db):
    client, db = client_and_db
    user = User(email="user@example.com", credits_remaining=3)
    db.add(user)
    db.commit()

    response = client.post("/api/auth/login", json={"email": " USER@example.com "})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["session_token"]
    assert data["credits_remaining"] == 3


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


def test_create_checkout_uses_configured_success_url(client_and_db, monkeypatch):
    client, _ = client_and_db
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(id="cs_test_checkout", url="https://checkout.stripe.test/pay")

    monkeypatch.setattr(billing.config, "STRIPE_SECRET_KEY", "sk_test")
    monkeypatch.setattr(billing.config, "FRONTEND_BASE_URL", "http://localhost:8501")
    monkeypatch.setattr(billing.stripe.checkout.Session, "create", fake_create)

    response = client.post(
        "/api/billing/create-checkout",
        json={
            "email": " Buyer@Example.com ",
            "success_url": "https://ignored.example/success",
            "cancel_url": "https://ignored.example/cancel",
        },
    )

    assert response.status_code == 200
    assert response.json()["checkout_url"] == "https://checkout.stripe.test/pay"
    assert captured["customer_email"] == "buyer@example.com"
    assert captured["success_url"] == "http://localhost:8501?session_token={CHECKOUT_SESSION_ID}"
    assert captured["cancel_url"] == "http://localhost:8501"


def test_stripe_webhook_rejects_invalid_signature(client_and_db, monkeypatch):
    client, _ = client_and_db

    def fake_construct_event(payload, sig_header, secret):
        raise ValueError("bad signature")

    monkeypatch.setattr(billing.config, "STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setattr(billing.stripe.Webhook, "construct_event", fake_construct_event)

    response = client.post("/api/stripe/webhook", content=b"{}", headers={"stripe-signature": "bad"})

    assert response.status_code == 400


def test_webhook_grants_credits_once(client_and_db, monkeypatch):
    client, db = client_and_db
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_webhook",
                "payment_status": "paid",
                "customer_details": {"email": "paid@example.com"},
            }
        },
    }

    monkeypatch.setattr(billing.config, "STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setattr(billing.config, "CREDIT_PACK_SIZE", 10)
    monkeypatch.setattr(billing.stripe.Webhook, "construct_event", lambda payload, sig, secret: event)

    assert client.post("/api/stripe/webhook", content=b"{}", headers={"stripe-signature": "ok"}).status_code == 200
    assert client.post("/api/stripe/webhook", content=b"{}", headers={"stripe-signature": "ok"}).status_code == 200

    user = db.query(User).filter(User.email == "paid@example.com").one()
    record = db.query(CheckoutRecord).filter(CheckoutRecord.stripe_session_id == "cs_webhook").one()
    assert user.credits_remaining == 10
    assert record.status == "completed"


def test_exchange_after_webhook_issues_token_without_double_credit(client_and_db, monkeypatch):
    client, db = client_and_db
    user = User(email="paid@example.com", credits_remaining=10)
    record = CheckoutRecord(
        stripe_session_id="cs_paid",
        email="paid@example.com",
        status="completed",
        completed_at=utcnow(),
    )
    db.add_all([user, record])
    db.commit()

    checkout = SimpleNamespace(
        id="cs_paid",
        payment_status="paid",
        customer_details=SimpleNamespace(email="paid@example.com"),
        customer_email=None,
    )
    monkeypatch.setattr(billing.config, "STRIPE_SECRET_KEY", "sk_test")
    monkeypatch.setattr(billing.config, "CREDIT_PACK_SIZE", 10)
    monkeypatch.setattr(billing.stripe.checkout.Session, "retrieve", lambda session_id: checkout)

    response = client.post("/api/billing/exchange-session", json={"checkout_session_id": "cs_paid"})

    assert response.status_code == 200
    data = response.json()
    assert data["session_token"]
    assert data["credits_remaining"] == 10
    db.refresh(user)
    db.refresh(record)
    assert user.credits_remaining == 10
    assert record.status == "exchanged"


def test_exchange_before_webhook_grants_once_and_webhook_preserves_state(client_and_db, monkeypatch):
    client, db = client_and_db
    record = CheckoutRecord(stripe_session_id="cs_race", email="race@example.com", status="pending")
    db.add(record)
    db.commit()

    checkout = {
        "id": "cs_race",
        "payment_status": "paid",
        "customer_details": {"email": "race@example.com"},
    }
    monkeypatch.setattr(billing.config, "STRIPE_SECRET_KEY", "sk_test")
    monkeypatch.setattr(billing.config, "STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setattr(billing.config, "CREDIT_PACK_SIZE", 10)
    monkeypatch.setattr(billing.stripe.checkout.Session, "retrieve", lambda session_id: checkout)
    monkeypatch.setattr(
        billing.stripe.Webhook,
        "construct_event",
        lambda payload, sig, secret: {"type": "checkout.session.completed", "data": {"object": checkout}},
    )

    exchange = client.post("/api/billing/exchange-session", json={"checkout_session_id": "cs_race"})
    webhook = client.post("/api/stripe/webhook", content=b"{}", headers={"stripe-signature": "ok"})

    assert exchange.status_code == 200
    assert webhook.status_code == 200
    user = db.query(User).filter(User.email == "race@example.com").one()
    db.refresh(record)
    assert user.credits_remaining == 10
    assert record.status == "exchanged"
