import os
from collections.abc import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config.loguru_config import logger

DB_URL = ""
DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""

DB_CONFIG = ""

Base = declarative_base()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(DB_CONFIG)
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
            raise HTTPException(status_code=500, detail="Unexpected error") from error
        finally:
            await session.close()
