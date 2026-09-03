"""Shared test configuration and fixtures."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.db.base import Base
from app.core.config import get_settings


@pytest.fixture(scope="session")
def settings():
    """Get application settings."""
    return get_settings()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    # Use a test database URL
    test_db_url = "postgresql+psycopg://vanraksha:vanraksha@localhost:5432/vanraksha_test"
    
    engine = create_async_engine(test_db_url, echo=False, future=True)
    
    # Create tables
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


# Override the get_db dependency for tests
@pytest.fixture(autouse=True)
def override_get_db(db_session):
    """Override the database dependency for tests."""
    from app.db.session import get_db as original_get_db
    from app.main import app
    
    async def get_test_db():
        yield db_session
    
    app.dependency_overrides[original_get_db] = get_test_db
    yield
    app.dependency_overrides.clear()