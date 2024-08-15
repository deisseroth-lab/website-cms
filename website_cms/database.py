from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

import asyncio
from litestar import Litestar, get
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.plugins import AsyncSessionConfig, SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from .page import Page
from .site import Site
from .engine import engine

session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///test.sqlite",
    session_config=session_config,
    create_all=True
)  # Create 'async_session' dependency.


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def on_startup() -> None:
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # async with async_session() as session:
    async with sqlalchemy_config.get_engine().begin() as session:
        # initialize database
        # await session.run_sync(UUIDBase.metadata.create_all)

        await session.run_sync(UUIDBase.metadata.drop_all)
        await session.run_sync(UUIDBase.metadata.create_all)

        # async def init_models():
        #     async with async_session().begin() as conn:
        #     await conn.run_sync(Base.metadata.drop_all)
        #     await conn.run_sync(Base.metadata.create_all)

# asyncio.run(init_models())

    async with async_session() as session:
        # adds some dummy data if no data is present."""
        statement = select(func.count()).select_from(Site)
        count = await session.execute(statement)
        if not count.scalar():
            site_id = uuid.uuid4()
            session.add(
                Site(name="literary", url="http://deisseroth.org/", id=site_id)
            )
            session.add(Page(title="Index", site_id=site_id))

            site_id = uuid.uuid4()
            session.add(
                Site(
                    name="group",
                    url="https://web.stanford.edu/group/dlab/",
                    id=site_id
                )
            )
            session.add(Page(title="Index", site_id=site_id))
            await session.commit()
