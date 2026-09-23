"""
=========================================================
FlowForge - Activity Model
=========================================================

This file defines the Activity table in our database.

# NEW CONCEPT: Audit Logs / Activity Logs
# What it is: A record of actions taken by users in the system.
# Why it exists: To track who did what and when, which is crucial for 
# security, debugging, and providing administrators with visibility 
# into system usage.
"""

from datetime import datetime, UTC
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

class Activity(BaseModel):
    __tablename__ = "activities"

    # 1. Action performed (e.g., "User logged in", "User created topic")
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 2. Detailed description of the action
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 3. When the action occurred
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC), 
        nullable=False
    )

    # 4. Foreign Key linking to the users table
    # This stores the ID of the user who performed the action.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )

    # 5. SQLAlchemy Relationship
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="activities"
    )
