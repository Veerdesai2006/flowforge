"""
=========================================================
FlowForge - Project Repository
=========================================================
Handles all database (SQL) operations for Projects.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.project import Project

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    # 1. Create a new project
    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    # 2. Get a single project by ID
    def get_by_id(self, project_id: int) -> Project | None:
        statement = select(Project).where(Project.id == project_id)
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    # 3. Get all projects owned by a specific user!
    def get_all_for_user(self, user_id: int) -> list[Project]:
        statement = select(Project).where(Project.owner_id == user_id)
        result = self.db.execute(statement)
        return list(result.scalars().all())

    # 4. Update an existing project
    def update(self, project: Project) -> Project:
        self.db.commit()
        self.db.refresh(project)
        return project

    # 5. Delete a project
    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()
