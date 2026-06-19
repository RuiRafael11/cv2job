import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from api import config
from api.models import PaidSession, User, utcnow


@dataclass(frozen=True)
class Actor:
    tier: str
    user: User | None = None


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _bearer_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


def _owner_token(request: Request, body_owner_token: str | None) -> str | None:
    return (
        request.headers.get("X-Owner-Token")
        or _bearer_token(request)
        or request.cookies.get("OWNER_TOKEN")
        or body_owner_token
    )


def resolve_actor(
    request: Request,
    db: Session,
    owner_token: str | None = None,
    session_token: str | None = None,
) -> Actor:
    bearer = _bearer_token(request)
    supplied_owner_token = _owner_token(request, owner_token)
    if config.OWNER_TOKEN and supplied_owner_token:
        if hmac.compare_digest(supplied_owner_token, config.OWNER_TOKEN):
            return Actor(tier="owner")

    token = bearer or session_token or request.cookies.get("cv2job_session")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing owner token or paid session token.",
        )

    paid_session = db.query(PaidSession).filter(PaidSession.token_hash == hash_token(token)).first()
    if not paid_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token.")

    expires_at = paid_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session token expired.")

    paid_session.last_used_at = utcnow()
    db.commit()
    db.refresh(paid_session)
    return Actor(tier="paid", user=paid_session.user)


def consume_paid_credit(db: Session, actor: Actor) -> int | None:
    if actor.tier == "owner":
        return None
    if actor.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid paid session.")
    if actor.user.credits_remaining <= 0:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="No credits remaining.")

    actor.user.credits_remaining -= 1
    actor.user.updated_at = utcnow()
    db.commit()
    db.refresh(actor.user)
    return actor.user.credits_remaining
