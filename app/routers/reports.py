from fastapi import APIRouter, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from ..services import reports as reports_service
from ..services import locations as locations_service

reports_router = APIRouter()
templates = Jinja2Templates(directory="./app/templates")


@reports_router.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


@reports_router.get("/")
async def get_home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@reports_router.get("/reports")
async def get_reports(num_days: int = 1):
    reports = reports_service.get_reports(num_days=num_days)
    return {
        "reports": reports,
    }


@reports_router.get("/locations")
async def get_locations():
    locations_list = locations_service.get_locations()
    return {
        "locations": locations_list,
    }


@reports_router.post("/reports")
async def create_report(location_id: str):
    try:
        reports_service.create_report(location_id)
        location_reports = reports_service.get_reports_by_location(
            location_id=location_id, num_days=1
        )
        return {"reports": location_reports}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
