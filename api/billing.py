import secrets
from datetime import timedelta
from typing import Any

import stripe
from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from api import config
from api.auth import hash_token
from api.models import CheckoutRecord, PaidSession, User, utcnow


stripe.api_key = config.STRIPE_SECRET_KEY
CHECKOUT_PLACEHOLDER = "{CHECKOUT_SESSION_ID}"


def _require_stripe_key() -> None:
    if not config.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="STRIPE_SECRET_KEY is not configured.",
        )


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _checkout_return_url() -> str:
    frontend_url = config.FRONTEND_BASE_URL.rstrip("/")
    separator = "&" if "?" in frontend_url else "?"
    return f"{frontend_url}{separator}session_token={CHECKOUT_PLACEHOLDER}"


def _checkout_cancel_url() -> str:
    return config.FRONTEND_BASE_URL.rstrip("/") or "http://localhost:8501"


def _field(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _checkout_email(checkout: Any, fallback: str) -> str:
    customer_details = _field(checkout, "customer_details")
    email = _field(customer_details, "email") if customer_details else None
    customer_email = _field(checkout, "customer_email")
    normalized = _normalize_email(email or customer_email or fallback)
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Checkout session is missing customer email.")
    return normalized


def create_checkout_session(db: Session, email: str, success_url: str | None = None, cancel_url: str | None = None):
    _require_stripe_key()
    email = _normalize_email(email)
    checkout = stripe.checkout.Session.create(
        mode="payment",
        customer_email=email,
        success_url=_checkout_return_url(),
        cancel_url=_checkout_cancel_url(),
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": config.PRICE_CURRENCY,
                    "unit_amount": config.PRICE_AMOUNT_CENTS,
                    "product_data": {"name": config.PRODUCT_NAME},
                },
            }
        ],
        metadata={"credit_pack_size": str(config.CREDIT_PACK_SIZE)},
    )
    record = CheckoutRecord(
        stripe_session_id=checkout.id,
        email=email,
        status="pending",
    )
    db.add(record)
    db.commit()
    return checkout


def _get_or_create_user(db: Session, email: str) -> User:
    email = _normalize_email(email)
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(email=email, credits_remaining=0)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def issue_paid_session(db: Session, email: str, grant_credits: bool = True) -> tuple[str, User]:
    email = _normalize_email(email)
    user = _get_or_create_user(db, email)
    if grant_credits:
        user.credits_remaining += config.CREDIT_PACK_SIZE
    user.updated_at = utcnow()

    token = secrets.token_urlsafe(32)
    paid_session = PaidSession(
        user=user,
        token_hash=hash_token(token),
        expires_at=utcnow() + timedelta(days=config.PAID_SESSION_TTL_DAYS),
    )
    db.add(paid_session)
    db.commit()
    db.refresh(user)
    return token, user


def create_login_session(db: Session, email: str) -> tuple[str, User]:
    return issue_paid_session(db, _normalize_email(email), grant_credits=False)


def _find_or_create_checkout_record(db: Session, checkout: Any) -> CheckoutRecord:
    checkout_id = _field(checkout, "id")
    record = db.query(CheckoutRecord).filter(
        CheckoutRecord.stripe_session_id == checkout_id
    ).first()
    if record:
        return record

    record = CheckoutRecord(
        stripe_session_id=checkout_id,
        email=_checkout_email(checkout, ""),
        status="pending",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _finalize_paid_checkout(db: Session, checkout: Any, mark_exchanged: bool = False) -> User:
    checkout_id = _field(checkout, "id")
    if not checkout_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Checkout session is missing an id.")
    if _field(checkout, "payment_status") != "paid":
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Checkout is not paid.")

    record = _find_or_create_checkout_record(db, checkout)
    email = _checkout_email(checkout, record.email)
    grant_credits = record.status not in {"completed", "exchanged"}

    user = _get_or_create_user(db, email)
    if grant_credits:
        user.credits_remaining += config.CREDIT_PACK_SIZE
        user.updated_at = utcnow()

    record.email = email
    record.status = "exchanged" if mark_exchanged or record.status == "exchanged" else "completed"
    record.completed_at = record.completed_at or utcnow()
    db.commit()
    db.refresh(user)
    return user


def exchange_checkout_session(db: Session, checkout_session_id: str) -> tuple[str, User]:
    _require_stripe_key()
    record = db.query(CheckoutRecord).filter(
        CheckoutRecord.stripe_session_id == checkout_session_id
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown checkout session.")
    checkout = stripe.checkout.Session.retrieve(checkout_session_id)
    user = _finalize_paid_checkout(db, checkout, mark_exchanged=True)
    return issue_paid_session(db, user.email, grant_credits=False)


async def handle_stripe_webhook(request: Request, db: Session) -> dict[str, str]:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if config.STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, config.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError) as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook.") from exc
    else:
        event = stripe.Event.construct_from(await request.json(), stripe.api_key)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        _finalize_paid_checkout(db, session)
    return {"status": "ok"}
