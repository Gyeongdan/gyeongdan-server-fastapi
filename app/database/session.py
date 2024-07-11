import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config.loguru_config import logger

Base = declarative_base()

load_dotenv()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "gyeongdan")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_CONFIG = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
# DB_CONFIG = "postgresql+asyncpg://localhost:5432/gyeongdan"

engine = create_async_engine(DB_CONFIG)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        try:
            yield session
            await session.commit()
        except HTTPException as error:
            await session.rollback()
            logger.error(f"HTTP exception: {error}")
            raise error
        except Exception as error:
            await session.rollback()
            logger.error(f"Unexpected error: {error}")
            raise HTTPException(
                status_code=500, detail="Unexpected error"
            ) from error  # pylint: disable=line-too-long
        finally:
            await session.close()
