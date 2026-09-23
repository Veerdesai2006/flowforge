from app.models.board import Board
from app.models.user import User
from app.repositories.board import BoardRepository
from app.repositories.project import ProjectRepository
from app.schemas.board import BoardCreate, BoardUpdate
from app.services.activity import ActivityService
from app.repositories.activity import ActivityRepository

class BoardService:
    def __init__(self, board_repository: BoardRepository, project_repository: ProjectRepository):
        self.board_repository = board_repository
        self.project_repository = project_repository
        self.activity_service = ActivityService(ActivityRepository(board_repository.db))

    def _verify_project_access(self, project_id: int, current_user: User):
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found.")
        if project.owner_id != current_user.id:
            raise PermissionError("You do not have permission to access this project.")
        return project

    def create_board(self, data: BoardCreate, current_user: User) -> Board:
        self._verify_project_access(data.project_id, current_user)
        
        board = Board(
            name=data.name,
            description=data.description,
            project_id=data.project_id
        )
        created = self.board_repository.create(board)
        self.activity_service.log_activity(
            user_id=current_user.id,
            action="Created Board",
            description=f"Created board '{created.name}'"
        )
        return created

    def get_project_boards(self, project_id: int, current_user: User) -> list[Board]:
        self._verify_project_access(project_id, current_user)
        return self.board_repository.get_all_for_project(project_id)

    def get_board_by_id(self, board_id: int, current_user: User) -> Board:
        board = self.board_repository.get_by_id(board_id)
        if not board:
            raise ValueError("Board not found.")
            
        # Ensure the user has access to the project this board belongs to
        self._verify_project_access(board.project_id, current_user)
        return board

    def update_board(self, board_id: int, data: BoardUpdate, current_user: User) -> Board:
        board = self.get_board_by_id(board_id, current_user)
        
        if data.name is not None:
            board.name = data.name
        if data.description is not None:
            board.description = data.description
            
        updated = self.board_repository.update(board)
        self.activity_service.log_activity(
            user_id=current_user.id,
            action="Updated Board",
            description=f"Updated board '{updated.name}'"
        )
        return updated

    def delete_board(self, board_id: int, current_user: User) -> None:
        board = self.get_board_by_id(board_id, current_user)
        self.board_repository.delete(board)
        self.activity_service.log_activity(
            user_id=current_user.id,
            action="Deleted Board",
            description=f"Deleted board '{board.name}'"
        )
