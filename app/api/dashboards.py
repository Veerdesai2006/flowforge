"""
=========================================================
FlowForge - Dashboards API
=========================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_admin, require_super_admin
from app.services.dashboard import DashboardService
from app.schemas.dashboard import UserDashboardResponse, AdminDashboardResponse, SuperAdminDashboardResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/user", response_model=UserDashboardResponse)
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard data for normal users.
    Returns their topics, tasks, and activity.
    """
    service = DashboardService(db)
    return service.get_user_dashboard(current_user)


@router.get("/admin", response_model=AdminDashboardResponse)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    # RBAC: Only ADMINs and SUPER_ADMINs can access this endpoint
    current_admin: User = Depends(require_admin)
):
    """
    Get dashboard data for administrators.
    Returns stats for normal users and system activity.
    """
    service = DashboardService(db)
    return service.get_admin_dashboard(current_admin)


@router.get("/super-admin", response_model=SuperAdminDashboardResponse)
def get_super_admin_dashboard(
    db: Session = Depends(get_db),
    # RBAC: ONLY SUPER_ADMINs can access this endpoint
    current_super_admin: User = Depends(require_super_admin)
):
    """
    Get system-wide dashboard data for Super Admins.
    """
    service = DashboardService(db)
    return service.get_super_admin_dashboard(current_super_admin)
