"""
FlowForge Models Package

Purpose
-------
Import every SQLAlchemy model here so that Alembic can
discover them when generating migrations.

Whenever you create a new model, import it below.
"""

from app.models.user import User
from app.models.token_blocklist import TokenBlocklist

# Future models
# from app.models.project import Project
# from app.models.board import Board
# from app.models.task import Task
# from app.models.comment import Comment
# from app.models.attachment import Attachment
# from app.models.notification import Notification

__all__ = [
    "User",
]