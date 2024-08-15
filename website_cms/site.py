from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

import asyncio
from litestar import Litestar
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase

from .engine import engine

class Site(UUIDAuditBase):
    """Site model representing a website

    The `UUIDAuditBase` class includes a `UUID` based primary key (`id`) and 2
    additional columns: `created_at` and `updated_at`. `created_at` is a
    timestamp of when the record created, and `updated_at` is the last time the
    record was modified."""
    __tablename__ = "site"

    name: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str]
    pages: Mapped[list[Page]] = relationship(
        back_populates="site", lazy="selectin"
    )

    def __repr__(self):
        return f"Site(id={self.id!r}, name={self.name!r}, url={self.url!r})"


@dataclass
class SiteData:
    name: str
    url: str


async def get_sites():
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        # statement = select(Site)
        # result = await session.execute(statement)
        # sites : list[Site] = result.scalars().all()
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
        print(result)
        site : Site = result.one_or_none()
        if site:
            site = site[0]
            return site

    return None


async def create_site(site: SiteData, async_session: async_sessionmaker[AsyncSession]=None) -> Site:

    if not async_session:
        async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        site_id = uuid.uuid4()
        site = Site(name=site.name, url=site.url, id=site_id)
        session.add(site)
        await session.commit()

    return site


async def upload_site(site: Site, async_session: async_sessionmaker[AsyncSession]=None) -> Site:

    if not async_session:
        async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # TODO add uploaded_at field
        # site.uploaded_at = time.now()
        # session.add(site)
        # await session.commit()
        pass

    print("UPLOADING SITE!")

    return site
