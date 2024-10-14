from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import UUID, ForeignKey, select, UniqueConstraint
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

import asyncio
from litestar import Litestar
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase

from .git import GitRepo
from .engine import engine
from .site import Site


class Page(UUIDAuditBase):
    """ Page model representing one page in a website.
    """

    title: Mapped[str]

    # do we need these with git? maybe, if we want different title/file names
    # html_file_object_id: Mapped[text??]
    # css_file_object_id: Mapped[text??]

    site_id: Mapped[UUID] = mapped_column(ForeignKey("site.id"))
    site: Mapped[Site] = relationship(
        lazy="joined", innerjoin=True, viewonly=True
    )

    __table_args__ = (UniqueConstraint('site_id', 'title', name='site_id_title_uc'),                     )


@dataclass
class PageData:
    title: str
    html: str = ""
    css: str = ""


async def create_page(site: Site, page: PageData, async_session: async_sessionmaker[AsyncSession]=None) -> Page:

    if not async_session:
        async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        page_id = uuid.uuid4()
        page = Page(title=page.title, id=page_id, site_id=site.id)
        session.add(page)
        await session.commit()

    return page


async def get_page_by_title(site: Site, title: str, async_session: async_sessionmaker[AsyncSession]=None) -> Page:

    if not async_session:
        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            q = select(Page).join(Site).where(Site.name == site.name and Page.title == title)
            result = await session.execute(q)
            page: Page = result.first()
            # page : Page = result.one_or_none()
            if page:
                page = page[0]
            return page

    return None


async def save_page(page: Page, page_data: PageData, async_session: async_sessionmaker[AsyncSession]=None) -> Page:

    repo = GitRepo(page.site.name)
    repo.update_files([
        (f"{page_data.title}.html", page_data.html),
        (f"{page_data.title}.css", page_data.css)
    ])
    repo.add()
    repo.commit()
    # repo.push() # this should push to a remote branch, but not start an upload process yet

    print("PAGE HTML AND CSS SAVED")
    print(page_data.title)
    print(page_data.html)

    return page
