"""
=========================================================
FlowForge - View Routes
=========================================================

This router is responsible for rendering HTML pages
using Jinja2 templates.

Unlike REST APIs that return JSON, these routes
return HTML pages.
"""

# ======================================================
# Imports
# ======================================================

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

# ======================================================
# Templates
# ======================================================

templates = Jinja2Templates(directory="app/templates")

# ======================================================
# Router
# ======================================================

router = APIRouter(
    tags=["Views"]
)

# ======================================================
# Home Page
# ======================================================

@router.get("/")
def home(request: Request):
    """
    Render the Home page.

    Every TemplateResponse MUST receive
    the request object.
    """

    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={}
    )


# ======================================================
# Login Page
# ======================================================

@router.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={}
    )


# ======================================================
# Register Page
# ======================================================

@router.get("/register")
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={}
    )


# ======================================================
# Dashboard
# ======================================================

@router.get("/dashboard")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard/dashboard.html",
        context={}
    )