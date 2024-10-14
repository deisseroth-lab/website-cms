from pathlib import Path

from typing import Annotated, Any

from litestar import Litestar, get, post
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Template
from litestar.response.redirect import Redirect
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from litestar.exceptions import NotFoundException

from .database import on_startup

from .site import Site, SiteData, get_sites, get_site_by_name, create_site, upload_site
from .page import Page, PageData, create_page, get_page_by_title, save_page

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
            "site": site,
            }
        )

@get("/sites/create")
async def sites_create() -> Template:
    return Template(
        template_name="sites/create.html.j2",
        context={}
    )


@post(path="/sites/create")
async def sites_create_post(#data: dict[str, str]) -> dict[str, str]:
    data: Annotated[SiteData, Body(media_type=RequestEncodingType.URL_ENCODED)],
) -> Redirect:

    print(data)
    site = await create_site(data)
    print(site)

    return Redirect("/")


@get(path="/sites/{site_name:str}/upload")
async def sites_upload(site_name:str) -> Template:

    site = await get_site_by_name(site_name)

    if not site:
        raise NotFoundException

    return Template(
        template_name="sites/upload.html.j2",
        context={
            "site_name": site_name,
        }
    )



@post(path="/sites/{site_name:str}/upload")
async def sites_upload_post(site_name:str) -> Redirect:

    site = await get_site_by_name(site_name)

    if not site:
        raise NotFoundException

    site = await upload_site(site)

    return Redirect("/")


@get("/sites/{site_name:str}/pages/{page_name:str}/edit")
async def pages_edit(site_name:str, page_name:str) -> Template:

    site = await get_site_by_name(site_name)
    page = await get_page_by_title(site, page_name)

    return Template(
        template_name="pages/edit.html.j2",
        context={"site": site, "page": page}
    )


@get("/sites/{site_name:str}/pages/create")
async def pages_create(site_name:str) -> Template:

    site = await get_site_by_name(site_name)
    print(site)

    if not site:
        raise NotFoundException

    return Template(
        template_name="pages/create.html.j2",
        context={"site": site}
    )


@post("/sites/{site_name:str}/pages/create")
async def pages_create_post(
    site_name: str,
    data: Annotated[PageData, Body(media_type=RequestEncodingType.URL_ENCODED)],
) -> Redirect:

    site = await get_site_by_name(site_name)

    page = await create_page(site, data)


    return Redirect(f"/sites/{site_name}")

@post("/sites/{site_name:str}/pages/{page_name:str}/save")
async def pages_save_post(
    site_name: str, page_name: str,
    data: Annotated[PageData, Body(media_type=RequestEncodingType.JSON)],
) -> bool:

    site = await get_site_by_name(site_name)
    page = await get_page_by_title(site, page_name)

    print(site)
    print(page)

    page = await save_page(page, data)

    return True
    # return Redirect("/")

@get(
    "/sites/{site_name:str}/pages/{page_name:str}/load",
    media_type="application/json"
)
async def pages_load() -> dict[str, Any]:
    return {
        "projects": [{
            "id": 1,
            "data": {
                "assets": [],
                "styles": [],
                "pages": [{
                    "component": "<div>Initial content</div>"
                }]
            }
        }]
    }



app = Litestar(
    route_handlers=[
        sites, sites_view, sites_create, sites_create_post,
        sites_upload, sites_upload_post,
        pages_edit, pages_create, pages_create_post, pages_save_post, pages_load,
        create_static_files_router(path="/", directories=["public"]),
    ],
    on_startup=[on_startup],
    template_config=TemplateConfig(
        directory=Path("templates"), engine=JinjaTemplateEngine
    )
)
