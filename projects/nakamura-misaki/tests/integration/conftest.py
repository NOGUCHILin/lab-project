"""Integration test fixtures"""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.manager import DatabaseManager


@pytest.fixture(scope="session")
def database_url() -> str:
    """Get test database URL from environment or use default

    Returns:
        Test database URL
    """
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki_test",
    )


@pytest_asyncio.fixture(scope="session")
async def db_manager(database_url: str) -> AsyncGenerator[DatabaseManager, None]:
    """Create database manager for tests

    Args:
        database_url: Database connection URL

    Yields:
        DatabaseManager instance
    """
    manager = DatabaseManager(database_url, echo=False)

    # Create tables at start of test session
    await manager.create_tables()

    yield manager

    # Drop tables and close connection at end
    await manager.drop_tables()
    await manager.close()


@pytest_asyncio.fixture
async def db_session(db_manager: DatabaseManager) -> AsyncGenerator[AsyncSession, None]:
    """Get database session for a single test

    Args:
        db_manager: DatabaseManager instance

    Yields:
        AsyncSession for testing
    """
    async with db_manager.session() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()
