# cv2job SaaS

cv2job is a Streamlit CV optimizer backed by a FastAPI API. The UI keeps the original ATS wizard and Harvard PDF flow, while the backend owns AI keys, Stripe billing, paid sessions, and usage credits.

## Architecture

- **Streamlit frontend (`app.py`)**: collects CV/job inputs, keeps the existing wizard/dashboard layout, and calls FastAPI endpoints.
- **FastAPI backend (`api/main.py`)**: authenticates owner or paid requests, routes AI calls, creates Stripe Checkout sessions, exchanges paid checkouts for session tokens, and generates PDFs.
- **SQLite**: stores paid users, checkout records, hashed session tokens, and remaining credits.
- **AI routing**:
  - Owner requests use `GOOGLE_API_KEY` and `gemini-2.5-flash`.
  - Paid requests use `OPENROUTER_API_KEY` and `google/gemma-2-9b-it`.

## Environment

Copy `.env.example` to `.env` or export these variables:

```env
GOOGLE_API_KEY=          # Gemini key (owner tier)
OPENROUTER_API_KEY=      # OpenRouter key (paid tier)
OWNER_TOKEN=             # Secret token that bypasses payment
STRIPE_SECRET_KEY=       # Stripe secret
STRIPE_PUBLISHABLE_KEY=  # Stripe publishable key
STRIPE_WEBHOOK_SECRET=   # Stripe webhook
DATABASE_URL=sqlite:///cv2job.db
```

Optional pricing/model overrides:

```env
FRONTEND_BASE_URL=http://localhost:8501
OWNER_MODEL=gemini-2.5-flash
PAID_MODEL=google/gemma-2-9b-it
CREDIT_PACK_SIZE=10
PRICE_AMOUNT_CENTS=900
PRICE_CURRENCY=eur
ENABLE_UNVERIFIED_EMAIL_LOGIN=false
```

`ENABLE_UNVERIFIED_EMAIL_LOGIN=true` is only for local development/demo recovery flows. In production, keep it disabled and use the Stripe Checkout flow below. `STRIPE_WEBHOOK_SECRET` should be configured in production so webhook events are signature-verified.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn api.main:app --reload
```

Start Streamlit in a second terminal:

```bash
streamlit run app.py
```

The Streamlit sidebar defaults to `http://127.0.0.1:8000` for the backend API.

## Local Demo Checklist

1. Start FastAPI and Streamlit.
2. Paste a CV and job description to run the free ATS preview.
3. Choose the CV output language: `English` or `Português`.
4. Enter an email in the sidebar and click **Comprar 10 creditos**.
5. Complete Stripe Checkout and return to Streamlit with `session_token={CHECKOUT_SESSION_ID}`.
6. Streamlit calls `POST /api/billing/exchange-session`, stores the paid session token, and shows the active email plus remaining credits.
7. Use **Verificar sessao** in the sidebar to refresh `/api/session/status` if needed.
8. Generate the optimized Markdown CV and export the Harvard PDF.

## Owner Flow

1. Enter the server `OWNER_TOKEN` in the Streamlit sidebar.
2. Streamlit sends it as `Authorization: Bearer <OWNER_TOKEN>`; the backend also accepts `X-Owner-Token`.
3. FastAPI compares it to the env token using constant-time comparison.
4. Owner requests skip Stripe and usage checks.
5. AI requests run with `GOOGLE_API_KEY`.

Do not expose `OWNER_TOKEN` in a public frontend. It is intended for trusted local/admin use only.

## Paid Flow

Recommended production flow:

1. Enter an email and click **Comprar 10 creditos**.
2. Streamlit asks FastAPI to create a Stripe Checkout Session.
3. Stripe redirects back with `session_token={CHECKOUT_SESSION_ID}`.
4. Streamlit exchanges that checkout session id through `POST /api/billing/exchange-session`.
5. FastAPI issues a paid session token and stores only its SHA-256 hash.
6. Paid ATS/PDF endpoints require the token; `POST /api/optimize` consumes one credit.

`POST /api/auth/login` is disabled by default because it creates a session from an email without proving ownership of that inbox. Enable it only for local development/demo by setting `ENABLE_UNVERIFIED_EMAIL_LOGIN=true`.

The Streamlit sidebar shows the current session state, email, credit balance, and a **Verificar sessao** action backed by `POST /api/session/status`.

For local Stripe webhooks:

```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

## API Endpoints

- `GET /api/health`
- `POST /api/auth/login` (disabled by default; dev/demo only)
- `POST /api/billing/create-checkout`
- `POST /api/billing/exchange-session`
- `POST /api/stripe/webhook`
- `POST /api/billing/webhook` (compatibility alias)
- `POST /api/session/status`
- `POST /api/ats-score`
- `POST /api/agent-review`
- `POST /api/optimize`
- `POST /api/generate-cv`

Authenticated AI/PDF endpoints accept either `X-Owner-Token`, `Authorization: Bearer <paid-session-token>`, or matching token fields in the JSON body.

## CV Output Language

The optimizer supports two output languages:

- `en` — English, default
- `pt` — Portuguese

Streamlit exposes this as **English / Português**. The selected `language` is sent to `POST /api/optimize` and `POST /api/generate-cv`. The PDF generator renders the optimized Markdown it receives, so section headings and prose come from the optimizer output.

## Tests

```bash
pytest
```

The tests cover deterministic ATS scoring shape, preserved optimizer prompt rules, EN/PT output language handling, owner token auth, paid token auth and credit consumption, guarded email login, Stripe checkout/exchange behavior, and PDF byte generation.
