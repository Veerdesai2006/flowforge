from app.models.task import Task
from app.models.user import User
from app.repositories.task import TaskRepository
from app.repositories.board import BoardRepository
from app.repositories.project import ProjectRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.activity import ActivityService
from app.repositories.activity import ActivityRepository

class TaskService:
    def __init__(self, task_repo: TaskRepository, board_repo: BoardRepository, project_repo: ProjectRepository):
        self.task_repo = task_repo
        self.board_repo = board_repo
        self.project_repo = project_repo
        self.activity_service = ActivityService(ActivityRepository(task_repo.db))

    def _verify_board_access(self, board_id: int, user: User):
        board = self.board_repo.get_by_id(board_id)
        if not board:
            raise ValueError("Board not found.")
        project = self.project_repo.get_by_id(board.project_id)
        if not project or project.owner_id != user.id:
            raise PermissionError("No access to this board.")
        return board

    def create_task(self, data: TaskCreate, user: User) -> Task:
        self._verify_board_access(data.board_id, user)
        task = Task(
            title=data.title,
            description=data.description,
            board_id=data.board_id,
            priority=data.priority,
        )
        created = self.task_repo.create(task)
        self.activity_service.log_activity(
            user_id=user.id,
            action="Created Task",
            description=f"Created task '{created.title}'"
        )
        return created

    def get_board_tasks(
        self, 
        board_id: int, 
        user: User, 
        status: str | None = None, 
        page: int = 1, 
        page_size: int = 10
    ) -> dict:
        self._verify_board_access(board_id, user)
        items, total_items = self.task_repo.get_all_for_board(board_id, status, page, page_size)
        total_pages = (total_items + page_size - 1) // page_size
        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages if total_pages > 0 else 1
        }

    def update_task(self, task_id: int, data: TaskUpdate, user: User) -> Task:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Task not found.")
        self._verify_board_access(task.board_id, user)
        
        status_changed = False
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None and task.status != data.status:
            task.status = data.status
            status_changed = True
        if data.priority is not None:
            task.priority = data.priority
            
        updated = self.task_repo.update(task)
        
        if status_changed:
            self.activity_service.log_activity(
                user_id=user.id,
                action="Updated Task Status",
                description=f"Moved task '{updated.title}' to {updated.status}"
            )
        else:
            self.activity_service.log_activity(
                user_id=user.id,
                action="Updated Task",
                description=f"Updated task '{updated.title}'"
            )
            
        return updated

    def delete_task(self, task_id: int, user: User) -> None:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Task not found.")
        self._verify_board_access(task.board_id, user)
        self.task_repo.delete(task)
        self.activity_service.log_activity(
            user_id=user.id,
            action="Deleted Task",
            description=f"Deleted task '{task.title}'"
        )
