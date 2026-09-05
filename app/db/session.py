"""
مدیریت اتصال دیتابیس با SQLAlchemy Async
از Connection Pooling استفاده می‌کنه تا زیر بار زیاد هم پایدار بمونه
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # چک سلامت کانکشن قبل از استفاده
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """کلاس پایه‌ی همه‌ی مدل‌ها"""
    pass


async def get_db() -> AsyncSession:
    """Dependency برای تزریق سشن دیتابیس به endpoint ها"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
