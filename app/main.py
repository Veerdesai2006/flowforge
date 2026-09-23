"""
=========================================================
FlowForge - Main Application
=========================================================
Application Entry Point
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.api.views import router as views_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.projects import router as projects_router
from app.api.boards import router as boards_router
from app.api.tasks import router as tasks_router
from app.api.upload import router as upload_router
from app.api.dashboards import router as dashboards_router

app = FastAPI(title="FlowForge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(views_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(boards_router)
app.include_router(tasks_router)
app.include_router(upload_router)
app.include_router(dashboards_router)

templates = Jinja2Templates(directory="app/templates")
