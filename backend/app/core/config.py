from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application Mode
    APP_MODE: str = "offline"  # "offline" for SQLite, "live" for PostgreSQL
    
    # Database Configuration
    # SQLite (Offline Mode) - Default for development/testing
    SQLITE_DATABASE_URL: str = "sqlite:///./budget_tracker.db"
    
    # PostgreSQL (Live Mode) - For production/Docker
    POSTGRES_USER: str = "budget_user"
    POSTGRES_PASSWORD: str = "budget_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "budget_tracker"
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Dynamic database URL based on APP_MODE.
        Returns SQLite URL in offline mode, PostgreSQL URL in live mode.
        """
        if self.APP_MODE.lower() == "live":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            return self.SQLITE_DATABASE_URL
    
    @property
    def is_offline_mode(self) -> bool:
        """Check if application is running in offline mode"""
        return self.APP_MODE.lower() == "offline"
    
    @property
    def is_live_mode(self) -> bool:
        """Check if application is running in live mode"""
        return self.APP_MODE.lower() == "live"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Plaid API Configuration
    PLAID_CLIENT_ID: Optional[str] = None
    PLAID_SECRET: Optional[str] = None
    PLAID_ENV: str = "sandbox"  # sandbox, development, production
    PLAID_PRODUCTS: list = ["transactions", "accounts", "identity"]
    PLAID_COUNTRY_CODES: list = ["US"]
    
    # Encryption for sensitive data
    ENCRYPTION_KEY: Optional[str] = None
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SmartBudget API"
    
    # Performance Settings (mode-dependent)
    @property
    def DATABASE_POOL_SIZE(self) -> int:
        """Database connection pool size - only relevant for PostgreSQL"""
        return 5 if self.is_live_mode else 0
    
    @property
    def DATABASE_MAX_OVERFLOW(self) -> int:
        """Max overflow connections - only relevant for PostgreSQL"""
        return 10 if self.is_live_mode else 0
    
    @property
    def DATABASE_POOL_RECYCLE(self) -> int:
        """Connection recycle time in seconds - only relevant for PostgreSQL"""
        return 3600 if self.is_live_mode else -1
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()