"""
=========================================================
FlowForge - Activity Repository
=========================================================
"""

from typing import List
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.user import UserRole


class ActivityRepository:
    """
    Repository for all database operations related to the Activity model.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, activity: Activity) -> Activity:
        """
        Save a new activity into the database.
        """
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def get_by_user_id(self, user_id: int, limit: int = 50) -> List[Activity]:
        """
        Get recent activity for a specific user.
        """
        statement = select(Activity).where(Activity.user_id == user_id).order_by(desc(Activity.created_at)).limit(limit)
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def get_all(self, limit: int = 100) -> List[Activity]:
        """
        Get recent activity across the entire system.
        """
        statement = select(Activity).order_by(desc(Activity.created_at)).limit(limit)
        result = self.db.execute(statement)
        return list(result.scalars().all())
    
    def get_by_roles(self, allowed_roles: List[UserRole], limit: int = 100) -> List[Activity]:
        """
        Get recent activity filtered by the roles of the users who performed the actions.
        This is useful because ADMINs should only see USER activity, while SUPER_ADMINs
        can see both USER and ADMIN activity.
        """
        from app.models.user import User
        statement = (
            select(Activity)
            .join(User, Activity.user_id == User.id)
            .where(User.role.in_(allowed_roles))
            .order_by(desc(Activity.created_at))
            .limit(limit)
        )
        result = self.db.execute(statement)
        return list(result.scalars().all())
