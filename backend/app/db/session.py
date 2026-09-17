import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Normalize sqlite URL if testing locally
db_url = settings.DATABASE_URL
if "sqlite" in db_url and not db_url.startswith("sqlite+aiosqlite"):
    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")

# If testing environment and default postgres isn't running, fallback gracefully to aiosqlite for zero friction
is_local_dev = os.getenv("USE_SQLITE_DEV", "true").lower() == "true"
if is_local_dev and "postgresql" in db_url:
    dev_sqlite_path = os.path.join(os.path.dirname(__file__), "dev_securepdf.db")
    db_url = f"sqlite+aiosqlite:///{dev_sqlite_path}"

engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async SQLAlchemy session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Create all tables in the database if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
