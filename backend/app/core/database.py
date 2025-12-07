from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Configure engine parameters based on mode
def get_engine_config():
    """Get database engine configuration based on APP_MODE"""
    base_config = {
        "url": settings.DATABASE_URL,
    }
    
    if settings.is_offline_mode:
        # SQLite specific configuration
        logger.info("Initializing database in OFFLINE mode (SQLite)")
        base_config["connect_args"] = {"check_same_thread": False}
        base_config["echo"] = False  # Set to True for SQL debugging
    else:
        # PostgreSQL specific configuration
        logger.info("Initializing database in LIVE mode (PostgreSQL)")
        base_config["pool_size"] = settings.DATABASE_POOL_SIZE
        base_config["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        base_config["pool_recycle"] = settings.DATABASE_POOL_RECYCLE
        base_config["pool_pre_ping"] = True  # Verify connections before using
        base_config["echo"] = False  # Set to True for SQL debugging
    
    return base_config

# Create database engine with mode-appropriate settings
engine_config = get_engine_config()
engine = create_engine(**engine_config)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for SQLAlchemy models
Base = declarative_base()

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database - create all tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def check_db_connection():
    """Check if database connection is working"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info(f"Database connection successful ({settings.APP_MODE} mode)")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False