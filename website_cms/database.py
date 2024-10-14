from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from sqlalchemy import ForeignKey, func, MetaData, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

import asyncio
from litestar import Litestar, get
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.plugins import AsyncSessionConfig, SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from .page import Page
from .site import Site
from .engine import engine, DATABASE_URI

session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=DATABASE_URI,
    session_config=session_config,
    create_all=True
)

async def init_models():
    # initialize database
    async with sqlalchemy_config.get_engine().begin() as session:
        await session.run_sync(UUIDBase.metadata.drop_all)
        await session.run_sync(UUIDBase.metadata.create_all)

    return None

async def on_startup() -> None:
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # async with async_session() as session:
    async with sqlalchemy_config.get_engine().begin() as session:
        # initialize database

        # this will delete any data in existing database
        # await session.run_sync(UUIDBase.metadata.drop_all)

        await session.run_sync(UUIDBase.metadata.create_all)

    async with async_session() as session:
        # async with engine.connect() as conn:
        #     metadata = MetaData(schema='public')
        #     await conn.run_sync(metadata.reflect)
        # print(metadata.tables)

        # adds seed data if none is present
        # TODO move to separate seed.py file
        statement = select(func.count()).select_from(Site)
        count = await session.execute(statement)
        if not count.scalar():
            site_id = uuid.uuid4()
            session.add(
                Site(
                    name="literary",
                    url="http://deisseroth.org/",
                    id=site_id,
                    type="Static"
                )
            )
            session.add(Page(title="Index", site_id=site_id))

            site_id = uuid.uuid4()
            session.add(
                Site(
                    name="group",
                    url="https://web.stanford.edu/group/dlab/",
                    id=site_id,
                    type="Static"
                )
            )
            session.add(Page(title="Index", site_id=site_id))
            await session.commit()
