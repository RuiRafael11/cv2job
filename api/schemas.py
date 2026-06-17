from typing import Any

from pydantic import BaseModel


class WizardContext(BaseModel):
    q1: str = "N/A"
    q2: str = "N/A"
    q3: str = "N/A"


class AuthenticatedRequest(BaseModel):
    owner_token: str | None = None
    session_token: str | None = None


class AtsScoreRequest(AuthenticatedRequest):
    cv: str
    job: str
    context: WizardContext


class OptimizeRequest(AuthenticatedRequest):
    cv: str
    job: str
    ats: dict[str, Any]
    context: WizardContext


class GenerateCvRequest(AuthenticatedRequest):
    markdown: str


class OptimizeResponse(BaseModel):
    markdown: str
    credits_remaining: int | None = None


class GenerateCvResponse(BaseModel):
    pdf_base64: str


class CheckoutCreateRequest(BaseModel):
    email: str
    success_url: str
    cancel_url: str


class CheckoutCreateResponse(BaseModel):
    checkout_url: str
    checkout_session_id: str


class CheckoutExchangeRequest(BaseModel):
    checkout_session_id: str


class CheckoutExchangeResponse(BaseModel):
    session_token: str
    email: str
    credits_remaining: int


class SessionStatusRequest(BaseModel):
    session_token: str


class SessionStatusResponse(BaseModel):
    email: str
    credits_remaining: int


class LoginRequest(BaseModel):
    email: str


class LoginResponse(BaseModel):
    session_token: str
    email: str
    credits_remaining: int
