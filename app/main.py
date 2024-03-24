from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from .routers import reports

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(reports.reports_router, tags=["reports"])
