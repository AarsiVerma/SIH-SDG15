"""Shared test configuration and fixtures."""
import os

# Force test settings BEFORE importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("ENV", "test")
os.environ.setdefault("DEBUG", "false")

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


def pytest_sessionstart(session):
    """Called before test collection starts."""
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
    os.environ.setdefault("ENV", "test")


@pytest.fixture(scope="session")
def settings():
    """Get application settings."""
    from app.core.config import get_settings
    return get_settings()


@pytest.fixture(scope="session")
def postgres_available():
    """Check if PostgreSQL is available for geo tests."""
    try:
        import asyncio
        engine = create_async_engine("postgresql+psycopg://postgres:postgres@localhost:5432/vanraksha")
        async def check():
            try:
                async with engine.connect() as conn:
                    await conn.execute("SELECT 1")
                return True
            except Exception:
                return False
            finally:
                await engine.dispose()
        return asyncio.run(check())
    except Exception:
        return False


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a test database engine (SQLite for non-geo tests)."""
    test_db_url = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(test_db_url, echo=False, future=True)
    
    # Create tables
    from app.db.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncSession:
    """Create a test database session with transaction rollback."""
    async with db_engine.connect() as conn:
        transaction = await conn.begin()
        session = async_sessionmaker(bind=conn, class_=AsyncSession, expire_on_commit=False)()
        
        yield session
        
        await session.close()
        await transaction.rollback()


# Override the get_db dependency for tests (request explicitly when needed)
@pytest.fixture
def override_get_db(db_session):
    """Override the database dependency for tests."""
    from app.db.session import get_db as original_get_db
    from app.main import app
    
    async def get_test_db():
        yield db_session
    
    app.dependency_overrides[original_get_db] = get_test_db
    yield
    app.dependency_overrides.clear()


def pytest_configure(config):
    config.addinivalue_line("markers", "postgres: mark test as requiring PostgreSQL with PostGIS")
    config.addinivalue_line("markers", "integration: mark test as integration test requiring PostgreSQL")


def pytest_collection_modifyitems(config, items):
    """Auto-skip postgres tests if PostgreSQL not available."""
    # Check if postgres is available
    try:
        import asyncio
        engine = create_async_engine("postgresql+psycopg://postgres:postgres@localhost:5432/vanraksha")
        async def check():
            try:
                async with engine.connect() as conn:
                    await conn.execute("SELECT 1")
                return True
            except Exception:
                return False
            finally:
                await engine.dispose()
        pg_available = asyncio.run(check())
    except Exception:
        pg_available = False
    
    if not pg_available:
        skip_postgres = pytest.mark.skip(reason="PostgreSQL with PostGIS not available")
        for item in items:
            if "postgres" in item.keywords:
                item.add_marker(skip_postgres)