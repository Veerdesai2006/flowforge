"""
=========================================================
FlowForge - Main Application
=========================================================

Application Entry Point
"""

# =====================================================
# Imports
# =====================================================

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.views import router as views_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router

# =====================================================
# FastAPI App
# =====================================================

app = FastAPI(
    title="FlowForge",
    version="1.0.0",
)

# =====================================================
# Static Files
# =====================================================

"""
Anything inside

app/static

can be accessed from the browser.

Example

app/static/css/style.css

↓

/static/css/style.css
"""

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)
app.include_router(views_router)
app.include_router(auth_router)
app.include_router(users_router)
# =====================================================
# Jinja Templates
# =====================================================

"""
Jinja2Templates tells FastAPI where all HTML
templates are stored.

We'll use

templates.TemplateResponse()

to render pages.
"""

templates = Jinja2Templates(
    directory="app/templates",
)

# =====================================================
# Root Route
# =====================================================

@app.get("/")
def home():
    return {
        "message": "Welcome to FlowForge"
    }
