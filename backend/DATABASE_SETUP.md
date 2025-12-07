# Database Configuration Guide

SmartBudget supports two database modes to provide flexibility for different deployment scenarios:

## 🔄 Database Modes

### 1. **Offline Mode** (SQLite)
- **Best for**: Local development, testing, demos
- **Database**: SQLite (file-based)
- **Setup**: Zero configuration required
- **Pros**: Simple, portable, no server needed
- **Cons**: Limited concurrent access, not suitable for production

### 2. **Live Mode** (PostgreSQL)
- **Best for**: Production, staging, Docker deployments
- **Database**: PostgreSQL (server-based)
- **Setup**: Requires PostgreSQL server or Docker
- **Pros**: Full-featured, concurrent access, production-ready
- **Cons**: Requires additional setup

## 🚀 Quick Start

### Offline Mode (Default)

1. **Set environment variable** in `.env`:
   ```bash
   APP_MODE=offline
   ```

2. **Run the backend**:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Mac/Linux
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Database auto-creates**: SQLite file `budget_tracker.db` is created automatically

### Live Mode (PostgreSQL)

#### Option A: Using Docker Compose (Recommended)

1. **Set environment variable** in `.env`:
   ```bash
   APP_MODE=live
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_USER=budget_user
   POSTGRES_PASSWORD=budget_password
   POSTGRES_DB=budget_tracker
   ```

2. **Start services**:
   ```bash
   cd infra
   docker-compose up -d
   ```

3. **Backend connects automatically** to PostgreSQL container

#### Option B: Local PostgreSQL Installation

1. **Install PostgreSQL** on your system

2. **Create database**:
   ```sql
   CREATE DATABASE budget_tracker;
   CREATE USER budget_user WITH PASSWORD 'budget_password';
   GRANT ALL PRIVILEGES ON DATABASE budget_tracker TO budget_user;
   ```

3. **Set environment variables** in `.env`:
   ```bash
   APP_MODE=live
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=budget_user
   POSTGRES_PASSWORD=budget_password
   POSTGRES_DB=budget_tracker
   ```

4. **Run the backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

## 🔧 Configuration Details

### Environment Variables

| Variable | Offline Mode | Live Mode | Description |
|----------|-------------|-----------|-------------|
| `APP_MODE` | `offline` | `live` | Determines which database to use |
| `SQLITE_DATABASE_URL` | ✅ Used | ❌ Ignored | Path to SQLite database file |
| `POSTGRES_HOST` | ❌ Ignored | ✅ Used | PostgreSQL host address |
| `POSTGRES_PORT` | ❌ Ignored | ✅ Used | PostgreSQL port (default: 5432) |
| `POSTGRES_USER` | ❌ Ignored | ✅ Used | PostgreSQL username |
| `POSTGRES_PASSWORD` | ❌ Ignored | ✅ Used | PostgreSQL password |
| `POSTGRES_DB` | ❌ Ignored | ✅ Used | PostgreSQL database name |

### Connection Pooling (PostgreSQL Only)

In live mode, the application uses connection pooling for better performance:

- **Pool Size**: 5 connections
- **Max Overflow**: 10 additional connections
- **Pool Recycle**: 3600 seconds (1 hour)
- **Pre-Ping**: Enabled (validates connections before use)

## 📊 Database Schema

Both modes use the same schema. Tables are created automatically on first run:

- **users** - User accounts and authentication
- **bank_accounts** - Connected bank accounts (Plaid)
- **transactions** - Financial transactions
- **budgets** - User-defined budgets
- **plaid_link_sessions** - Plaid OAuth sessions

## 🔍 Verification

### Check Current Mode

```python
from app.core.config import settings

print(f"App Mode: {settings.APP_MODE}")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"Is Offline: {settings.is_offline_mode}")
print(f"Is Live: {settings.is_live_mode}")
```

### Test Database Connection

```python
from app.core.database import check_db_connection

if check_db_connection():
    print("✅ Database connection successful")
else:
    print("❌ Database connection failed")
```

## 🔄 Switching Modes

### From Offline to Live

1. Update `.env`:
   ```bash
   APP_MODE=live
   ```

2. Ensure PostgreSQL is running and accessible

3. **Data Migration** (if needed):
   ```bash
   # Export from SQLite
   sqlite3 budget_tracker.db .dump > backup.sql
   
   # Import to PostgreSQL (may require manual conversion)
   psql -U budget_user -d budget_tracker < backup_converted.sql
   ```

4. Restart application

### From Live to Offline

1. Update `.env`:
   ```bash
   APP_MODE=offline
   ```

2. Restart application (new SQLite database will be created)

## 🐛 Troubleshooting

### SQLite Issues

**Error**: `database is locked`
- **Cause**: Multiple processes accessing SQLite
- **Solution**: Use PostgreSQL for multi-user scenarios

**Error**: `table already exists`
- **Solution**: Delete `budget_tracker.db` and restart

### PostgreSQL Issues

**Error**: `could not connect to server`
- **Check**: PostgreSQL is running (`pg_ctl status` or `docker ps`)
- **Check**: Correct `POSTGRES_HOST` in `.env`
- **Check**: Firewall rules allow port 5432

**Error**: `password authentication failed`
- **Check**: Correct credentials in `.env`
- **Check**: User exists in PostgreSQL

**Error**: `database does not exist`
- **Solution**: Create database manually:
  ```bash
  psql -U postgres -c "CREATE DATABASE budget_tracker;"
  ```

## 📝 Best Practices

1. **Development**: Use offline mode for quick iteration
2. **Testing**: Use offline mode for unit tests, live mode for integration tests
3. **Staging**: Use live mode with Docker Compose
4. **Production**: Use live mode with managed PostgreSQL (RDS, Cloud SQL, etc.)
5. **Backups**: Always backup data before switching modes
6. **Security**: Never commit `.env` file; use strong passwords in production

## 🔐 Production Checklist

- [ ] Set `APP_MODE=live`
- [ ] Use managed PostgreSQL service
- [ ] Enable SSL/TLS for database connections
- [ ] Use strong passwords (minimum 16 characters)
- [ ] Restrict database access by IP
- [ ] Enable PostgreSQL logging
- [ ] Set up automated backups
- [ ] Monitor connection pool metrics
- [ ] Use read replicas for scaling (if needed)

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Plaid API Documentation](https://plaid.com/docs/)
