from asyncio import current_task
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session, AsyncSession

from app.config import config as settings

engine = create_async_engine(f'sqlite+aiosqlite://{settings.sqlite_path}',
                             connect_args={'check_same_thread': False},
                             echo=settings.dev_mode)
scoped_session = async_scoped_session(
    session_factory=async_sessionmaker(bind=engine, expire_on_commit=False),
    scopefunc=current_task
)


async def session_factory() -> AsyncGenerator[AsyncSession, None]:
    session = scoped_session()

    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
