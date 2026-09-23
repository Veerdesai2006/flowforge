"""
=========================================================
FlowForge - Dashboard Service
=========================================================
"""
from datetime import datetime, timedelta, UTC
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.project import Project
from app.models.board import Board
from app.models.task import Task, TaskStatus
from app.services.activity import ActivityService
from app.repositories.activity import ActivityRepository
from app.schemas.dashboard import UserDashboardResponse, AdminDashboardResponse, SuperAdminDashboardResponse


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.activity_service = ActivityService(ActivityRepository(db))

    def get_user_dashboard(self, current_user: User) -> UserDashboardResponse:
        # Count Topics (Projects) owned by user
        my_topics = self.db.scalar(
            select(func.count(Project.id)).where(Project.owner_id == current_user.id)
        ) or 0
        
        # Count Boards inside those topics
        my_boards = self.db.scalar(
            select(func.count(Board.id))
            .join(Project, Board.project_id == Project.id)
            .where(Project.owner_id == current_user.id)
        ) or 0
        
        # Count Tasks assigned to user
        my_tasks = self.db.scalar(
            select(func.count(Task.id)).where(Task.assignee_id == current_user.id)
        ) or 0
        
        completed_tasks = self.db.scalar(
            select(func.count(Task.id)).where(
                Task.assignee_id == current_user.id,
                Task.status == TaskStatus.DONE
            )
        ) or 0
        
        running_tasks = self.db.scalar(
            select(func.count(Task.id)).where(
                Task.assignee_id == current_user.id,
                Task.status == TaskStatus.IN_PROGRESS
            )
        ) or 0
        
        # We don't have a POSTPONED status in the db currently, 
        # so we'll just count TODO as postponed/backlog for this demo
        postponed_tasks = self.db.scalar(
            select(func.count(Task.id)).where(
                Task.assignee_id == current_user.id,
                Task.status == TaskStatus.TODO
            )
        ) or 0
        
        recent_activity = self.activity_service.get_dashboard_activity(current_user)
        
        return UserDashboardResponse(
            my_topics=my_topics,
            my_boards=my_boards,
            my_tasks=my_tasks,
            completed_tasks=completed_tasks,
            running_tasks=running_tasks,
            postponed_tasks=postponed_tasks,
            recent_activity=recent_activity
        )

    def get_admin_dashboard(self, current_user: User) -> AdminDashboardResponse:
        # Admins only care about normal users
        total_users = self.db.scalar(
            select(func.count(User.id)).where(User.role == UserRole.USER)
        ) or 0
        
        active_users = self.db.scalar(
            select(func.count(User.id)).where(
                User.role == UserRole.USER,
                User.is_active == True
            )
        ) or 0
        
        inactive_users = total_users - active_users
        
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
        recent_users = self.db.scalar(
            select(func.count(User.id)).where(
                User.role == UserRole.USER,
                User.created_at >= thirty_days_ago
            )
        ) or 0
        
        permitted_activity = self.activity_service.get_dashboard_activity(current_user)
        
        return AdminDashboardResponse(
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users,
            recent_users=recent_users,
            permitted_activity=permitted_activity
        )

    def get_super_admin_dashboard(self, current_user: User) -> SuperAdminDashboardResponse:
        total_users = self.db.scalar(
            select(func.count(User.id)).where(User.role == UserRole.USER)
        ) or 0
        
        total_admins = self.db.scalar(
            select(func.count(User.id)).where(User.role == UserRole.ADMIN)
        ) or 0
        
        total_super_admins = self.db.scalar(
            select(func.count(User.id)).where(User.role == UserRole.SUPER_ADMIN)
        ) or 0
        
        active_users = self.db.scalar(
            select(func.count(User.id)).where(User.is_active == True)
        ) or 0
        
        total_all = total_users + total_admins + total_super_admins
        inactive_users = total_all - active_users
        
        recent_activity = self.activity_service.get_dashboard_activity(current_user)
        
        return SuperAdminDashboardResponse(
            total_users=total_users,
            total_admins=total_admins,
            total_super_admins=total_super_admins,
            active_users=active_users,
            inactive_users=inactive_users,
            recent_activity=recent_activity
        )
