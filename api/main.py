import base64

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from api import billing
from api.ai_clients import AIClientError, client_for_tier
from api.auth import consume_paid_credit, resolve_actor
from api.db import get_db, init_db
from api.schemas import (
    AtsScoreRequest,
    CheckoutCreateRequest,
    CheckoutCreateResponse,
    CheckoutExchangeRequest,
    CheckoutExchangeResponse,
    GenerateCvRequest,
    GenerateCvResponse,
    LoginRequest,
    LoginResponse,
    OptimizeRequest,
    OptimizeResponse,
    SessionStatusRequest,
    SessionStatusResponse,
)
from pdf.harvard import convert_markdown_to_harvard_pdf
from services.ats import compute_local_ats, run_ats_analysis
from services.optimizer import build_optimize_prompts, strip_markdown_fences


app = FastAPI(title="cv2job API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/billing/create-checkout", response_model=CheckoutCreateResponse)
def create_checkout(payload: CheckoutCreateRequest, db: Session = Depends(get_db)):
    checkout = billing.create_checkout_session(
        db=db,
        email=str(payload.email),
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
    )
    return CheckoutCreateResponse(checkout_url=checkout.url, checkout_session_id=checkout.id)


@app.post("/api/billing/exchange-session", response_model=CheckoutExchangeResponse)
def exchange_session(payload: CheckoutExchangeRequest, db: Session = Depends(get_db)):
    token, user = billing.exchange_checkout_session(db, payload.checkout_session_id)
    return CheckoutExchangeResponse(
        session_token=token,
        email=user.email,
        credits_remaining=user.credits_remaining,
    )


@app.post("/api/stripe/webhook")
@app.post("/api/billing/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    return await billing.handle_stripe_webhook(request, db)


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token, user = billing.create_login_session(db, payload.email.strip().lower())
    return LoginResponse(
        session_token=token,
        email=user.email,
        credits_remaining=user.credits_remaining,
    )


@app.post("/api/session/status", response_model=SessionStatusResponse)
def session_status(payload: SessionStatusRequest, request: Request, db: Session = Depends(get_db)):
    actor = resolve_actor(request, db, session_token=payload.session_token)
    if actor.user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner sessions do not have credits.")
    return SessionStatusResponse(email=actor.user.email, credits_remaining=actor.user.credits_remaining)


@app.post("/api/ats-score")
def ats_score(payload: AtsScoreRequest, request: Request, db: Session = Depends(get_db)):
    def free_preview():
        local = compute_local_ats(payload.cv, payload.job)
        return {
            **local,
            "diagnostic": "Preview gratuito: o CV foi pontuado localmente. Gera o CV otimizado para receber a versao completa.",
            "next_steps": [
                {
                    "impact": "high",
                    "title": "Reforcar termos da vaga",
                    "bullets": [
                        "Revê os termos em falta e inclui apenas os que forem verdadeiros.",
                        "Prioriza palavras-chave que apareçam repetidamente na descricao da vaga.",
                    ],
                }
            ],
        }

    try:
        actor = resolve_actor(request, db, payload.owner_token, payload.session_token)
    except HTTPException:
        return free_preview()
    if actor.tier != "owner":
        return free_preview()
    try:
        return run_ats_analysis(
            client_for_tier(actor.tier),
            payload.cv,
            payload.job,
            payload.context.dict(),
        )
    except AIClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize(payload: OptimizeRequest, request: Request, db: Session = Depends(get_db)):
    actor = resolve_actor(request, db, payload.owner_token, payload.session_token)
    credits_remaining = consume_paid_credit(db, actor)
    try:
        sys_prompt, user_prompt = build_optimize_prompts(
            payload.cv,
            payload.job,
            payload.ats,
            payload.context.dict(),
        )
        markdown = client_for_tier(actor.tier).generate_text(
            user_prompt,
            system_instruction=sys_prompt,
            temperature=0.2,
            max_output_tokens=8192,
        )
        return OptimizeResponse(
            markdown=strip_markdown_fences(markdown),
            credits_remaining=credits_remaining,
        )
    except AIClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@app.post("/api/generate-cv", response_model=GenerateCvResponse)
def generate_cv(payload: GenerateCvRequest, request: Request, db: Session = Depends(get_db)):
    resolve_actor(request, db, payload.owner_token, payload.session_token)
    pdf_bytes = convert_markdown_to_harvard_pdf(payload.markdown)
    return GenerateCvResponse(pdf_base64=base64.b64encode(pdf_bytes).decode("ascii"))
