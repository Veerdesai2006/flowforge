"""
=========================================================
FlowForge - Project Model
=========================================================
This file defines the Project table in our database.
"""

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

class Project(BaseModel):
    __tablename__ = "projects"

    # 1. Basic details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Text allows for longer strings than String()
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 2. Foreign Key linking to the users table
    # This stores the ID of the user who owns this project.
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )

    # 3. SQLAlchemy Relationship
    # This doesn't create a column in the database!
    # It just allows us to type `project.owner.first_name` in our Python code.
    owner: Mapped["User"] = relationship(
        "User", 
        back_populates="projects" # This matches the variable we'll add to the User model
    )

    boards: Mapped[list["Board"]] = relationship(
        "Board",
        back_populates="project",
        cascade="all, delete-orphan"
    )
