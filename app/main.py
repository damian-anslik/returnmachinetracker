from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

load_dotenv()

from .routers import reports

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(reports.reports_router, tags=["reports"])


@app.exception_handler(404)
async def http_exception_handler(_, __):
    return RedirectResponse("/")
