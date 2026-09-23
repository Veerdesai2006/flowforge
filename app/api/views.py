from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["Views"])

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html", context={})

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="auth/login.html", context={})

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="auth/register.html", context={})

@router.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard/dashboard.html", context={})

@router.get("/profile")
def profile_page(request: Request):
    return templates.TemplateResponse(request=request, name="profile/profile.html", context={})

@router.get("/projects/{project_id}/boards")
def boards_page(request: Request, project_id: int):
    return templates.TemplateResponse(request=request, name="dashboard/boards.html", context={"project_id": project_id})

@router.get("/boards/{board_id}/tasks")
def tasks_page(request: Request, board_id: int):
    return templates.TemplateResponse(request=request, name="dashboard/tasks.html", context={"board_id": board_id})