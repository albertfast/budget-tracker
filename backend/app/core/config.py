from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database
    # Default to SQLite for local development if not set in .env
    DATABASE_URL: str = "sqlite:///./budget_tracker.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Plaid API Configuration
    PLAID_CLIENT_ID: Optional[str] = None
    PLAID_SECRET: Optional[str] = None
    PLAID_ENV: str = "sandbox"  # sandbox, development, production
    PLAID_PRODUCTS: list = ["transactions", "auth"] # Changed from accounts, identity to standard products
    PLAID_COUNTRY_CODES: list = ["US"]
    
    # Encryption for sensitive data
    ENCRYPTION_KEY: Optional[str] = None
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SmartBudget API"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()