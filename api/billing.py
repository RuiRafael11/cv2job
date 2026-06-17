import secrets
from datetime import timedelta

import stripe
from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from api import config
from api.auth import hash_token
from api.models import CheckoutRecord, PaidSession, User, utcnow


stripe.api_key = config.STRIPE_SECRET_KEY


def _require_stripe_key() -> None:
    if not config.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="STRIPE_SECRET_KEY is not configured.",
        )


def create_checkout_session(db: Session, email: str, success_url: str, cancel_url: str):
    _require_stripe_key()
    checkout = stripe.checkout.Session.create(
        mode="payment",
        customer_email=email,
        success_url=success_url,
        cancel_url=cancel_url,
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
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(email=email, credits_remaining=0)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def issue_paid_session(db: Session, email: str, grant_credits: bool = True) -> tuple[str, User]:
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
    return issue_paid_session(db, email, grant_credits=False)


def exchange_checkout_session(db: Session, checkout_session_id: str) -> tuple[str, User]:
    _require_stripe_key()
    record = db.query(CheckoutRecord).filter(
        CheckoutRecord.stripe_session_id == checkout_session_id
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown checkout session.")
    if record.status == "exchanged":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Checkout session was already exchanged.")

    checkout = stripe.checkout.Session.retrieve(checkout_session_id)
    if checkout.payment_status != "paid":
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Checkout is not paid.")

    email = checkout.customer_details.email if checkout.customer_details else record.email
    record.email = email or record.email
    record.status = "exchanged"
    record.completed_at = utcnow()
    db.commit()
    return issue_paid_session(db, record.email)


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
        record = db.query(CheckoutRecord).filter(
            CheckoutRecord.stripe_session_id == session["id"]
        ).first()
        if record:
            record.status = "completed"
            record.completed_at = utcnow()
            if session.get("customer_details") and session["customer_details"].get("email"):
                record.email = session["customer_details"]["email"]
            db.commit()
    return {"status": "ok"}
