"""
=========================================================
FlowForge - User Model
=========================================================

This file defines the User table.

Every person who can log into FlowForge
will have one record in this table.

Examples

- Super Admin
- Admin
- Developer
- Tester
- Project Owner

Every other module will reference this table.
"""

from enum import Enum

from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Enum as SqlEnum

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


# =====================================================
# User Roles
# =====================================================

"""
Why Enum?

Instead of storing random strings like

"admin"

"Admin"

"ADMIN"

we restrict values to fixed choices.

Benefits

✔ Prevents invalid data

✔ Better autocomplete

✔ Easier validation
"""


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    USER = "USER"


# =====================================================
# User Model
# =====================================================


class User(BaseModel):

    """
    Database table name.
    """

    __tablename__ = "users"

    # -------------------------------------------------
    # Basic Information
    # -------------------------------------------------

    # -------------------------------------------------
    # Personal Information
    # -------------------------------------------------

    """
    We store first and last names separately.

    Advantages

    ✔ Better searching
    ✔ Better sorting
    ✔ Personalized greetings
    ✔ Easier profile management

    Whenever we need the full name,
    we can combine them.
    """

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    @property
    def full_name(self) -> str:
        """
        Returns the user's full name.

        Example

        first_name = "Veer"

        last_name = "Desai"

        ↓

        "Veer Desai"
        """

        return f"{self.first_name} {self.last_name}"

    email: Mapped[str] = mapped_column(
        String(255),

        unique=True,

        index=True,

        nullable=False,
    )

    # Never store plain text passwords.

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # -------------------------------------------------
    # Role
    # -------------------------------------------------

    role: Mapped[UserRole] = mapped_column(

        SqlEnum(UserRole),

        default=UserRole.USER,

        nullable=False,
    )

    # -------------------------------------------------
    # Account Status
    # -------------------------------------------------

    """
    Instead of deleting users,

    we can disable them.

    Example

    Employee leaves company

    ↓

    is_active = False

    Login is blocked

    Historical data remains.
    """

    is_active: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False,
    )

    """
    Email verification.

    Later, after registration,

    we'll send an email verification link.

    Until verified,

    this remains False.
    """

    is_verified: Mapped[bool] = mapped_column(

        Boolean,

        default=False,

        nullable=False,
    )

    # Profile image URL (stored as a path to the uploaded file)
    # If None, the frontend will use a default avatar.
    avatar_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )

    # Banner image URL (like YouTube channel art)
    # If None, the frontend will use a default gradient banner.
    banner_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )

    # -------------------------------------------------
    # Relationships
    # -------------------------------------------------
    
    """
    This creates a Python list of all projects this user owns.
    If we type `user.projects`, SQLAlchemy will automatically
    fetch them from the database!
    """
    
    # We use quotes around "Project" to avoid circular import errors!
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan" # If user is deleted, delete their projects too!
    )
    
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="assignee"
    )

    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="user",
        cascade="all, delete-orphan"
    )