"""
=========================================================
FlowForge - SQLAlchemy Base Class
=========================================================

WHY THIS FILE EXISTS
--------------------

Every SQLAlchemy model (User, Project, Task, etc.)
needs a common parent class.

Instead of repeating common fields like

id
created_at
updated_at

inside every model,

we define them once here.

Benefits

✅ No code duplication
✅ Consistent table structure
✅ Easier maintenance
✅ Alembic can detect all models

Every model will inherit from BaseModel.

Example

class User(BaseModel):
    ...

class Project(BaseModel):
    ...

class Task(BaseModel):
    ...
"""

# =====================================================
# Imports
# =====================================================

from datetime import datetime, timezone

# timezone
# --------
# We use timezone-aware timestamps instead of naive timestamps.
#
# UTC is the standard used by almost every production application.
#
# Always store UTC in the database.
#
# Frontend can convert UTC to the user's local timezone.


from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


# =====================================================
# Base
# =====================================================

"""
DeclarativeBase

This is a NEW feature introduced in SQLAlchemy 2.0.

Older versions used

declarative_base()

SQLAlchemy 2.0 recommends subclassing DeclarativeBase.

Every database model inherits from this class.
"""


class Base(DeclarativeBase):
    pass


# =====================================================
# BaseModel
# =====================================================

"""
BaseModel

Contains common columns shared by every table.

Instead of writing

id

created_at

updated_at

inside every model,

we define them once.
"""


class BaseModel(Base):
    """
    This tells SQLAlchemy:

    Don't create a table for BaseModel.

    Only create tables for classes
    that inherit from BaseModel.
    """

    __abstract__ = True #This tells SQLAlchemy Don't make a table for this.

    # -------------------------------------------------
    # Primary Key
    # -------------------------------------------------

    id: Mapped[int] = mapped_column(

        primary_key=True,

        index=True,

        autoincrement=True,
    )

    # -------------------------------------------------
    # Created At
    # -------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        default=lambda: datetime.now(timezone.utc),

        nullable=False,
    )

    # -------------------------------------------------
    # Updated At
    # -------------------------------------------------

    updated_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        default=lambda: datetime.now(timezone.utc),

        # onupdate automatically updates this field
        # whenever a row is modified.
        onupdate=lambda: datetime.now(timezone.utc),

        nullable=False,
    )