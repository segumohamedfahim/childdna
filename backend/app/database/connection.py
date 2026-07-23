"""Database Connection - SQLAlchemy Engine and Session Management"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.config.settings import settings

# Convert postgresql:// to postgresql+asyncpg://
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database connection - validates connection"""
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def close_db() -> None:
    """Close database connection pool"""
    await engine.dispose()


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        yield session
