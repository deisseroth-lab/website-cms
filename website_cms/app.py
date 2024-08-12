from pathlib import Path

from typing import Annotated

from litestar import Litestar, get, post
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Template
from litestar.response.redirect import Redirect
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from litestar.exceptions import NotFoundException

from .models import Site, SiteData, on_startup, get_sites, get_site_by_name, create_site

@get("/")
async def sites() -> Template:
    """Index of all sites"""

    # load sites from db
    sites = await get_sites()
    # sites = [site[0] for site in sites]

    return Template(template_name="index.html.j2", context={"sites": sites})


@get("/sites/{site:str}")
async def sites_view(site:str) -> Template:

    site = await get_site_by_name(site)

    if not site:
        raise NotFoundException

    return Template(
        template_name="sites/view.html.j2",
        context={
            "site": site, "site_url": "http://localhost:8000"
            }
        )

@get("/sites/create")
def sites_create() -> Template:
    return Template(
        template_name="sites/create.html.j2",
        context={"site_url": "http://localhost:8000"}
        )

@get("/sites/{site:str}/pages/create")
async def pages_create(site:str) -> Template:

    site = await get_site_by_name(site)

    if not site:
        raise NotFoundException

    return Template(
        template_name="pages/create.html.j2",
        context={"site": site, "site_url": "http://localhost:8000"}
        )

@get("/sites/{site:str}/pages/{page:str}/edit")
def pages_edit() -> Template:
    return Template(
        template_name="pages/edit.html.j2",
        context={"site_url": "http://localhost:8000"}
        )

@post(path="/sites/create")
async def sites_create_post(#data: dict[str, str]) -> dict[str, str]:
    data: Annotated[SiteData, Body(media_type=RequestEncodingType.URL_ENCODED)],
) -> Redirect:

    create_site(data)

    return Redirect("/")


app = Litestar(
    route_handlers=[
        sites, sites_view, sites_create, sites_create_post, pages_create, pages_edit,
        create_static_files_router(path="/", directories=["public"]),
    ],
    on_startup=[on_startup],
    template_config=TemplateConfig(
        directory=Path("templates"), engine=JinjaTemplateEngine
    )
)
