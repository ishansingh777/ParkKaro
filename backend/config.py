import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres.isatsybreksmsliwmipj:Siddarth890@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"
    )
    api_port: int = int(os.getenv("API_PORT", 8000))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
    )
    jwt_secret: str = os.getenv("JWT_SECRET", "")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
    cookie_name: str = "pk_access_token"
    cookie_secure: bool = os.getenv("COOKIE_SECURE", "true").strip().lower() == "true"
    cookie_samesite: str = os.getenv("COOKIE_SAMESITE", "lax").strip().lower()
    login_rate_limit_max: int = int(os.getenv("LOGIN_RATE_LIMIT_MAX", 5))
    login_rate_limit_window_sec: int = int(os.getenv("LOGIN_RATE_LIMIT_WINDOW_SEC", 60))

    @property
    def cors_list(self):
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.database_url
        if ":6543/" in url:
            url = url.replace(":6543/", ":5432/")
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        if "sslmode=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}sslmode=require"
        return url


settings = Settings()
