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
```

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

## Owner Flow

1. Enter the server `OWNER_TOKEN` in the Streamlit sidebar.
2. Streamlit sends it as `X-Owner-Token`.
3. FastAPI compares it to the env token using constant-time comparison.
4. Owner requests skip Stripe and usage checks.
5. AI requests run with `GOOGLE_API_KEY`.

## Paid Flow

1. Enter an email in the sidebar and click **Comprar 10 creditos**.
2. Streamlit asks FastAPI to create a Stripe Checkout Session.
3. Stripe redirects back with `checkout_session_id`.
4. Streamlit exchanges that checkout id for a paid session token.
5. FastAPI stores only a SHA-256 hash of the session token.
6. Paid ATS/PDF endpoints require the token; `/api/optimize` consumes one credit.

For local Stripe webhooks:

```bash
stripe listen --forward-to localhost:8000/api/billing/webhook
```

## API Endpoints

- `GET /api/health`
- `POST /api/billing/create-checkout`
- `POST /api/billing/exchange-session`
- `POST /api/billing/webhook`
- `POST /api/session/status`
- `POST /api/ats-score`
- `POST /api/optimize`
- `POST /api/generate-cv`

Authenticated AI/PDF endpoints accept either `X-Owner-Token`, `Authorization: Bearer <paid-session-token>`, or matching token fields in the JSON body.

## Tests

```bash
pytest
```

The tests cover deterministic ATS scoring shape, preserved optimizer prompt rules, owner token auth, paid token auth and credit consumption, and PDF byte generation.
