from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from .core.config import settings
from .core.database import engine
from .models.database import Base
from .api import auth, banks, insights

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="SmartBudget API for personal finance management with bank integration"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8081"],  # React Native and web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok", "service": "SmartBudget API"}

# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(banks.router, prefix=f"{settings.API_V1_STR}/banks", tags=["bank-accounts"])
app.include_router(insights.router, prefix=f"{settings.API_V1_STR}/insights", tags=["financial-insights"])

@app.get("/")
def root():
    return {
        "message": "Welcome to SmartBudget API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
