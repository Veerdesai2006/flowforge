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
from app.models.project import Project
from app.models.board import Board
from app.models.task import Task
from app.models.activity import Activity
from app.models.task_embedding import TaskEmbedding

__all__ = [
    "User",
    "Project",
    "Board",
    "Task",
    "TokenBlocklist",
    "Activity",
    "TaskEmbedding",
]