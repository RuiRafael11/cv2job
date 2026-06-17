import os

from dotenv import load_dotenv


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OWNER_TOKEN = os.getenv("OWNER_TOKEN", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///cv2job.db")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:8501")

OWNER_MODEL = os.getenv("OWNER_MODEL", "gemini-2.5-flash")
PAID_MODEL = os.getenv("PAID_MODEL", "google/gemma-2-9b-it")

CREDIT_PACK_SIZE = int(os.getenv("CREDIT_PACK_SIZE", "10"))
PRICE_AMOUNT_CENTS = int(os.getenv("PRICE_AMOUNT_CENTS", "900"))
PRICE_CURRENCY = os.getenv("PRICE_CURRENCY", "eur")
PRODUCT_NAME = os.getenv("STRIPE_PRODUCT_NAME", "cv2job 10 CV optimization credits")

PAID_SESSION_TTL_DAYS = int(os.getenv("PAID_SESSION_TTL_DAYS", "30"))
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://github.com/RuiRafael11/cv2job")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "cv2job")
