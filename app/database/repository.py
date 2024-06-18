from typing import Any, Callable, Generic, Sequence, TypeVar

from fastapi import Depends, HTTPException
from sqlalchemy import BinaryExpression, Row, RowMapping, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from app.database.session import get_db_session

Base = declarative_base()
Model = TypeVar("Model", bound=Base)


class DatabaseRepository(Generic[Model]):
    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, data: dict) -> Model:
        async with (
            self.session.begin_nested()
            if self.session.in_transaction()
            else self.session.begin()
        ):
            try:
                instance = self.model(**data)
                self.session.add(instance)
                await self.session.flush()
                return instance
            except Exception as error:
                raise HTTPException(
                    status_code=500, detail="Unexpected error"
                ) from error

    async def get(self, pk: int) -> Model | None:
        async with (
            self.session.begin_nested()
            if self.session.in_transaction()
            else self.session.begin()
        ):
            try:
                instance = await self.session.get(self.model, pk)
                return instance
            except Exception as error:
                raise HTTPException(
                    status_code=500, detail="Unexpected error"
                ) from error

    async def delete(self, pk: int) -> None:
        async with (
            self.session.begin_nested()
            if self.session.in_transaction()
            else self.session.begin()
        ):
            try:
                instance = await self.get(pk)
                if instance:
                    await self.session.delete(instance)
            except Exception as error:
                raise HTTPException(
                    status_code=500, detail="Unexpected error"
                ) from error

    async def update_by_pk(self, pk: int, data: dict) -> Model:
        async with (
            self.session.begin_nested()
            if self.session.in_transaction()
            else self.session.begin()
        ):
            try:
                instance = await self.get(pk)

                for key, value in data.items():
                    setattr(instance, key, value)

                self.session.add(instance)
                return instance
            except Exception as error:
                raise HTTPException(
                    status_code=500, detail="Unexpected error"
                ) from error

    async def update(self, model: Generic[Model], data: dict) -> Model:
        async with (
            self.session.begin_nested()
            if self.session.in_transaction()
            else self.session.begin()
        ):
            try:
                for key, value in data.items():
                    setattr(model, key, value)

                self.session.add(model)
                return model
            except Exception as error:
                raise HTTPException(
                    status_code=500, detail="Unexpected error"
                ) from error

    async def filter(
        self, *expressions: BinaryExpression
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        async with (
            self.session.begin_nested()
            if self.session.in_transaction()
            else self.session.begin()
        ):
            query = (
                select(self.model)
                .filter(*expressions)
                .order_by(desc(self.model.id))  # pylint: disable=line-too-long
            )
            result = await self.session.execute(query)
            return result.scalars().all()


def get_repository(
    model: type[Base],
) -> Callable[[AsyncSession], DatabaseRepository[Base]]:
    def func(session: AsyncSession = Depends(get_db_session)):
        if session is None:
            raise HTTPException(status_code=500, detail="DB Connection Error")
        return DatabaseRepository(model, session)

    return func
