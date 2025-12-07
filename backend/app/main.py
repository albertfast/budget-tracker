from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .core.config import settings
from .core.database import init_db, check_db_connection, Base, engine
from .api import auth, insights  # banks temporarily disabled - needs database
from .api.plaid_legacy import router as plaid_legacy_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"Starting SmartBudget API in {settings.APP_MODE.upper()} mode")
logger.info(f"Database: {settings.DATABASE_URL}")

# Check database connection
if not check_db_connection():
    logger.warning("Database connection failed during startup")

# Initialize database tables
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="SmartBudget API for personal finance management with bank integration"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health():
    db_connected = check_db_connection()
    return {
        "status": "ok" if db_connected else "degraded",
        "service": "SmartBudget API",
        "mode": settings.APP_MODE,
        "database": "connected" if db_connected else "disconnected"
    }

# Routers
app.include_router(plaid_legacy_router, prefix="/api")

# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
# app.include_router(banks.router, prefix=f"{settings.API_V1_STR}/banks", tags=["bank-accounts"])  # Disabled - needs database
app.include_router(insights.router, prefix=f"{settings.API_V1_STR}/insights", tags=["financial-insights"])

@app.get("/")
def root():
    return {
        "message": "Welcome to SmartBudget API",
        "version": "1.0.0",
        "mode": settings.APP_MODE,
        "database": "SQLite" if settings.is_offline_mode else "PostgreSQL",
        "docs": "/docs",
        "health": "/health"
    }

@app.on_event("startup")
async def startup_event():
    """Run tasks on application startup"""
    logger.info("=" * 60)
    logger.info("SmartBudget API Started Successfully")
    logger.info(f"Mode: {settings.APP_MODE.upper()}")
    logger.info(f"Database: {'SQLite' if settings.is_offline_mode else 'PostgreSQL'}")
    logger.info(f"API Docs: http://localhost:8000/docs")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Run tasks on application shutdown"""
    logger.info("Shutting down SmartBudget API...")
    # Close database connections gracefully if engine exists
    try:
        if 'engine' in globals() and engine is not None:
            engine.dispose()
            logger.info("Database connections closed")
    except Exception as e:
        logger.warning(f"Could not dispose database engine: {e}")
