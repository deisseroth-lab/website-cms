from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

import asyncio
from litestar import Litestar, get
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.plugins import AsyncSessionConfig, SQLAlchemyAsyncConfig, SQLAlchemyPlugin


# the SQLAlchemy base includes a declarative model for you to use in your models.
# T
class Site(UUIDAuditBase):
    """Site model representing a website

    The `UUIDAuditBase` class includes a `UUID` based primary key (`id`) and 2
    additional columns: `created_at` and `updated_at`. `created_at` is a
    timestamp of when the record created, and `updated_at` is the last time the
    record was modified."""
    __tablename__ = "site"

    name: Mapped[str]
    url: Mapped[str]
    pages: Mapped[list[Page]] = relationship(
        back_populates="site", lazy="selectin"
    )

    def __repr__(self):
        return f"Site(id={self.id!r}, name={self.name!r}, url={self.url!r})"

class Page(UUIDAuditBase):
    """ Page model representing one page in a website.

    """

    title: Mapped[str]

    # html_file_object_id: Mapped[text??]
    # css_file_object_id: Mapped[text??]

    site_id: Mapped[UUID] = mapped_column(ForeignKey("site.id"))
    site: Mapped[Site] = relationship(
        lazy="joined", innerjoin=True, viewonly=True
    )


session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///test.sqlite",
    session_config=session_config,
    create_all=True
)  # Create 'async_session' dependency.


engine = create_async_engine("sqlite+aiosqlite:///test.sqlite", echo=True)


async def get_sites():
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        statement = select(Site)
        result = await session.execute(statement)
        sites : list[Site] = result.scalars().all()
        print(sites)
        statement = select("*").select_from(Site)
        sites = await session.execute(statement)
        return sites.all()

async def get_site(id, async_session: async_sessionmaker[AsyncSession]=None) -> Site:
    if not async_session:
        async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        site = await session.get(Site, id)
        print(site)
        return site

async def get_site_by_name(name, async_session: async_sessionmaker[AsyncSession]=None) -> Site:
    if not async_session:
        async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        q = select(Site).where(Site.name == name)
        result = await session.execute(q)
        site : Site = result.one_or_none()
        if site:
            site = site[0]
        return site

@dataclass
class SiteData:
    name: str
    url: str

async def create_site(site: SiteData, async_session: async_sessionmaker[AsyncSession]=None) -> Site:

    if not async_session:
        async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        site_id = uuid.uuid4()
        # site = Site(name=site.name, url=site.url, id=site_id)
        session.add(Site(name=site.name, url=site.url, id=site_id))
        await session.commit()

    return None

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
