"""
Shared test fixtures for API tests.
"""

# ruff: noqa: E402, I001

import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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
from app.database import Base  # Use the same Base instance  # noqa: E402
from app.models import (  # noqa: E402, I001
    Archetype,
    Enhancement,
    EnhancementSet,
    Power,
    Powerset,
)

# Import the app last
from main import app  # noqa: E402

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the get_db dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the get_db dependency
app.dependency_overrides[database.get_db] = override_get_db


@pytest.fixture
def client():
    """Create a test client with a fresh database."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    # Drop tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create a database session for tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


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
        short_name="Acc/Dam",
        description="Increases accuracy and damage",
        enhancement_type="set_piece",
        set_id=sample_enhancement_set.id,
        level_min=30,
        level_max=50,
        effect_type="accuracy_damage",
        effect_value=0.265,
        unique_per_build=False,
    )
    db_session.add(enhancement)
    db_session.commit()
    db_session.refresh(enhancement)
    return enhancement
