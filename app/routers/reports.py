from fastapi import APIRouter, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, PlainTextResponse

from ..services import reports as reports_service
from ..services import locations as locations_service
from ..services import sessions as sessions_service

reports_router = APIRouter()
templates = Jinja2Templates(directory="./app/templates")


@reports_router.get("/robots.txt", response_class=PlainTextResponse)
def get_robots_txt():
    data = """User-agent: *"""
    return data


@reports_router.get("/")
async def get_home(request: Request):
    session_id = request.cookies.get("session_id", sessions_service.create_session())
    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )
    response.set_cookie("session_id", session_id)
    return response


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
async def create_report(request: Request, location_id: str):
    session_id = request.cookies.get("session_id")
    if not session_id or not sessions_service.check_session_id_is_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session_id",
        )
    try:
        reports_service.create_report(location_id, session_id)
        location_reports = reports_service.get_reports_by_location(
            location_id=location_id, num_days=1
        )
        response = JSONResponse(
            content={"reports": location_reports},
        )
        response.set_cookie("session_id", session_id)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
