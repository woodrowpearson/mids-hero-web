"""
Shared test fixtures for API tests.
"""

# ruff: noqa: E402, I001

import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


# Mock asyncpg before importing anything that uses it
class MockAsyncpg:
    class Pool:
        pass


mock_asyncpg = MockAsyncpg()
sys.modules["asyncpg"] = mock_asyncpg


# Mock the async database functions
async def mock_create_database_pool():
    pass


async def mock_close_database_pool():
    pass


# Import database module first to get Base
from app import database  # noqa: E402

database.create_database_pool = mock_create_database_pool
database.close_database_pool = mock_close_database_pool

# Now import models - this will use the same Base from database module
from app.database import Base, get_db  # Use the same Base instance  # noqa: E402
from app.models import (  # noqa: E402, I001
    Archetype,
    Enhancement,
    EnhancementSet,
    Power,
    Powerset,
)

# Import the app last
from main import app  # noqa: E402

# Configure test database
# Check if we're running in CI with real PostgreSQL
if "DATABASE_URL" in os.environ and "test" in os.environ.get("DATABASE_URL", ""):
    # Use the real test database in CI
    SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]
    engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=StaticPool)
else:
    # Use in-memory SQLite for local tests
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a database session for tests."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create a new session for this test
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    # Rollback the transaction and close everything
    session.close()
    transaction.rollback()
    connection.close()

    # Drop all tables after test
    # Handle circular dependencies by dropping tables in the correct order
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        # SQLite doesn't enforce foreign keys by default, so we can drop all at once
        Base.metadata.drop_all(bind=engine)
    else:
        # For PostgreSQL, drop tables in reverse dependency order
        # First drop tables with foreign keys
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS build_powers CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS build_enhancements CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS builds CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS recipe_salvage CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS recipes CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS salvage CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS attribute_modifiers CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS type_grades CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS set_bonuses CASCADE"))
            conn.execute(
                text("DROP TABLE IF EXISTS power_enhancement_compatibility CASCADE")
            )
            conn.execute(text("DROP TABLE IF EXISTS power_prerequisites CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS enhancements CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS enhancement_sets CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS powers CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS powersets CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS archetypes CASCADE"))


@pytest.fixture
def client(db):
    """Create a test client with a fresh database."""

    # Override the get_db dependency to use our test db
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear the override after the test
    app.dependency_overrides.clear()


# Keep db_session as alias for backward compatibility
@pytest.fixture
def db_session(db):
    """Alias for db fixture for backward compatibility."""
    return db


@pytest.fixture
def sample_archetype(db_session):
    """Create a sample archetype for testing."""
    archetype = Archetype(
        name="Blaster",
        display_name="Blaster",
        description="Ranged damage dealer",
        hit_points_base=1000,
        hit_points_max=1606,
        primary_group="damage",
        secondary_group="support",
    )
    db_session.add(archetype)
    db_session.commit()
    db_session.refresh(archetype)
    return archetype


@pytest.fixture
def sample_powerset(db_session, sample_archetype):
    """Create a sample powerset for testing."""
    powerset = Powerset(
        name="Fire Blast",
        display_name="Fire Blast",
        description="Wield fire to blast your foes",
        archetype_id=sample_archetype.id,
        powerset_type="primary",
        icon_path="fire_blast.png",
    )
    db_session.add(powerset)
    db_session.commit()
    db_session.refresh(powerset)
    return powerset


@pytest.fixture
def sample_power(db_session, sample_powerset):
    """Create a sample power for testing."""
    power = Power(
        name="Fire Blast",
        display_name="Fire Blast",
        description="Hurl a blast of fire at your target",
        powerset_id=sample_powerset.id,
        power_type="attack",
        target_type="enemy",
        level_available=1,
        accuracy=1.0,
        damage_scale=1.0,
        endurance_cost=5.2,
        recharge_time=4.0,
        activation_time=1.67,
        range_feet=80,
        max_targets=1,
        icon_path="fire_blast.png",
    )
    db_session.add(power)
    db_session.commit()
    db_session.refresh(power)
    return power


@pytest.fixture
def sample_enhancement_set(db_session):
    """Create a sample enhancement set for testing."""
    enhancement_set = EnhancementSet(
        name="Devastation",
        display_name="Devastation",
        description="Ranged damage enhancement set",
        min_level=30,
        max_level=50,
    )
    db_session.add(enhancement_set)
    db_session.commit()
    db_session.refresh(enhancement_set)
    return enhancement_set


@pytest.fixture
def sample_enhancement(db_session, sample_enhancement_set):
    """Create a sample enhancement for testing."""
    enhancement = Enhancement(
        name="Devastation: Accuracy/Damage",
        display_name="Devastation: Accuracy/Damage",
        enhancement_type="set_piece",
        set_id=sample_enhancement_set.id,
        level_min=30,
        level_max=50,
        accuracy_bonus=26.5,
        damage_bonus=26.5,
        unique_enhancement=False,
    )
    db_session.add(enhancement)
    db_session.commit()
    db_session.refresh(enhancement)
    return enhancement
