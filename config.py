import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "techhelp-dev-secret-key-change-in-production")
    
    # Manejo de URI de base de datos compatible con Render/PostgreSQL y SQLite
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'techhelp.db'}")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_ID_PRO = os.getenv("STRIPE_PRICE_ID_PRO", "price_pro_monthly")
    
    # AI Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
    
    # App Settings
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")
    FREE_TIER_DAILY_LIMIT = int(os.getenv("FREE_TIER_DAILY_LIMIT", "5"))
    
    # Default Admin
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@techhelp.ia")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123456!")
    ADMIN_NAME = os.getenv("ADMIN_NAME", "Administrador TechHelp")
