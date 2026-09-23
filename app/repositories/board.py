from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.board import Board

class BoardRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, board: Board) -> Board:
        self.db.add(board)
        self.db.commit()
        self.db.refresh(board)
        return board

    def get_by_id(self, board_id: int) -> Board | None:
        statement = select(Board).where(Board.id == board_id)
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    def get_all_for_project(self, project_id: int) -> list[Board]:
        statement = select(Board).where(Board.project_id == project_id)
        result = self.db.execute(statement)
        return list(result.scalars().all())

    def update(self, board: Board) -> Board:
        self.db.commit()
        self.db.refresh(board)
        return board

    def delete(self, board: Board) -> None:
        self.db.delete(board)
        self.db.commit()
