from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config_data.config import config

# инстанция БД
engine = create_async_engine(url=f'sqlite+aiosqlite:///{config.database}', echo=False)
session_factory = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass


async def create_tables():
    async with engine.begin() as conn:
        from .models import User
        await conn.run_sync(Base.metadata.create_all)