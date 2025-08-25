"""
Database configuration and connection management for Mids-Web backend.
"""

import os

import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mids_web"
)

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Global connection pool
_connection_pool: asyncpg.Pool | None = None


async def create_database_pool():
    """Create database connection pool."""
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={"jit": "off"},
            )
            print("Database pool created successfully")
        except Exception as e:
            print(f"Failed to create database pool: {e}")
            raise


async def close_database_pool():
    """Close database connection pool."""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.close()
        _connection_pool = None
        print("Database pool closed")


async def get_db_connection():
    """Get database connection from pool."""
    global _connection_pool
    if _connection_pool is None:
        await create_database_pool()
    return await _connection_pool.acquire()


async def release_db_connection(connection):
    """Release database connection back to pool."""
    global _connection_pool
    if _connection_pool and connection:
        await _connection_pool.release(connection)


def get_db():
    """Get database session (for synchronous operations)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check function
async def check_database_health():
    """Check database connectivity."""
    try:
        conn = await get_db_connection()
        await conn.execute("SELECT 1")
        await release_db_connection(conn)
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False
