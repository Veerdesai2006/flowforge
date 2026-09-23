from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.task import Task

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: int) -> Task | None:
        stmt = select(Task).where(Task.id == task_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all_for_board(
        self, 
        board_id: int, 
        status: str | None = None, 
        page: int = 1, 
        page_size: int = 10
    ) -> tuple[list[Task], int]:
        from sqlalchemy import func
        
        # Base query to filter by board
        base_query = select(Task).where(Task.board_id == board_id)
        
        # Optional filter by status
        if status:
            base_query = base_query.where(Task.status == status)
            
        # COUNT tells PostgreSQL to count the total rows without returning them
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_items = self.db.execute(count_stmt).scalar_one()
        
        # OFFSET tells PostgreSQL how many rows to skip based on the page number
        # LIMIT tells PostgreSQL how many rows to return (page_size)
        # We order by updated_at and id to ensure stable pagination
        stmt = (
            base_query
            .order_by(Task.updated_at.desc(), Task.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        items = list(self.db.execute(stmt).scalars().all())
        return items, total_items

    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
