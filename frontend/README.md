# cv2job frontend

Next.js frontend for the cv2job FastAPI backend.

## Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

The frontend runs at:

```txt
http://localhost:3000
```

## Backend

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

The default backend URL is:

```txt
http://localhost:8000
```

## Environment

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For Stripe redirects to return directly to the wizard, set the backend
`FRONTEND_BASE_URL` to:

```env
FRONTEND_BASE_URL=http://localhost:3000/app
```

The frontend uses the existing backend endpoints:

- `POST /api/ats-score`
- `POST /api/agent-review`
- `POST /api/optimize`
- `POST /api/generate-cv`
- `POST /api/billing/create-checkout`
- `POST /api/billing/exchange-session`

PDF and DOCX CV files are parsed in the browser before being sent to the backend
as text.

Step 3 calls the ATS score endpoint first, then AI Agent Review when the backend
is available. If the agent review fails, the wizard keeps working with the ATS
score alone.
