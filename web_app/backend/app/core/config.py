from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import secrets

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PDF Table Extractor"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./pdf_extractor.db"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf"]
    UPLOAD_DIR: str = "uploads"
    
    # Rate Limiting (files per month by tier)
    FREE_TIER_LIMIT: int = 5
    BASIC_TIER_LIMIT: int = 50
    PRO_TIER_LIMIT: int = 200
    ENTERPRISE_TIER_LIMIT: int = -1  # Unlimited
    
    # External Services
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_FREE: Optional[str] = None  # Free tier (for downgrades)
    STRIPE_PRICE_BASIC: Optional[str] = None  # Basic plan price ID
    STRIPE_PRICE_PRO: Optional[str] = None    # Pro plan price ID
    STRIPE_PRICE_ENTERPRISE: Optional[str] = None  # Enterprise plan price ID
    
    # Email (for notifications)
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@pdfextractor.com"
    FROM_NAME: str = "PDF Extractor"
    FRONTEND_URL: str = "http://localhost:3500"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()