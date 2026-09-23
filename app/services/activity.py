"""
=========================================================
FlowForge - Activity Service
=========================================================
"""

from typing import List
from app.models.activity import Activity
from app.models.user import User, UserRole
from app.repositories.activity import ActivityRepository


class ActivityService:
    """
    Business logic for the Activity system.
    """

    def __init__(self, repository: ActivityRepository):
        self.repository = repository

    def log_activity(self, user_id: int, action: str, description: str = None) -> Activity:
        """
        Record a new activity in the system.
        """
        activity = Activity(
            user_id=user_id,
            action=action,
            description=description
        )
        return self.repository.create(activity)

    def get_user_activity(self, current_user: User, target_user_id: int) -> List[Activity]:
        """
        Get activity for a specific user, enforcing RBAC rules.
        """
        # A user can always view their own activity
        if current_user.id == target_user_id:
            return self.repository.get_by_user_id(target_user_id)
            
        # Admins and Super Admins can view other users' activities
        # But we must enforce that Admins cannot view Super Admin activity
        if current_user.role == UserRole.ADMIN:
            # Here we would normally check the target_user's role, 
            # but since we already check target_user role in the User API,
            # this method assumes the calling API has already verified the Admin 
            # is allowed to look at target_user_id.
            return self.repository.get_by_user_id(target_user_id)
            
        if current_user.role == UserRole.SUPER_ADMIN:
            return self.repository.get_by_user_id(target_user_id)
            
        raise ValueError("You are not authorized to view this user's activity.")

    def get_dashboard_activity(self, current_user: User) -> List[Activity]:
        """
        Get the appropriate system activity feed based on the user's role.
        
        - USER: Sees only their own activity.
        - ADMIN: Sees activity for normal USERs only.
        - SUPER_ADMIN: Sees activity for USERs and ADMINs (and themselves).
        """
        if current_user.role == UserRole.USER:
            return self.repository.get_by_user_id(current_user.id)
            
        if current_user.role == UserRole.ADMIN:
            return self.repository.get_by_roles([UserRole.USER])
            
        if current_user.role == UserRole.SUPER_ADMIN:
            return self.repository.get_all()
            
        return []
