from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
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
    
    class Config:
        env_file = ".env"

settings = Settings()