from app.models.project import Project
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.activity import ActivityService
from app.repositories.activity import ActivityRepository

class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository
        self.activity_service = ActivityService(ActivityRepository(repository.db))

    def create_project(self, data: ProjectCreate, current_user: User) -> Project:
        project = Project(
            name=data.name,
            description=data.description,
            owner_id=current_user.id
        )
        created = self.repository.create(project)
        self.activity_service.log_activity(
            user_id=current_user.id,
            action="Created Topic",
            description=f"Created topic '{created.name}'"
        )
        return created

    def get_user_projects(self, current_user: User) -> list[Project]:
        return self.repository.get_all_for_user(current_user.id)

    def get_project_by_id(self, project_id: int, current_user: User) -> Project:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found.")
        if project.owner_id != current_user.id:
            raise PermissionError("You do not have permission to access this project.")
        return project

    def update_project(self, project_id: int, data: ProjectUpdate, current_user: User) -> Project:
        project = self.get_project_by_id(project_id, current_user)
        if data.name is not None:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
            
        updated = self.repository.update(project)
        self.activity_service.log_activity(
            user_id=current_user.id,
            action="Updated Topic",
            description=f"Updated topic '{updated.name}'"
        )
        return updated

    def delete_project(self, project_id: int, current_user: User) -> None:
        project = self.get_project_by_id(project_id, current_user)
        self.repository.delete(project)
        self.activity_service.log_activity(
            user_id=current_user.id,
            action="Deleted Topic",
            description=f"Deleted topic '{project.name}'"
        )
