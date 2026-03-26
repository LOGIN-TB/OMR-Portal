from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import AppConfig

engine = None
async_session_factory = None


def init_db(config: AppConfig):
    global engine, async_session_factory
    engine = create_async_engine(config.database_url, echo=False)
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def close_db():
    if engine:
        await engine.dispose()
