from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.task import TaskRepository
from app.repositories.board import BoardRepository
from app.repositories.project import ProjectRepository
from app.services.task import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, PaginatedTaskResponse
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

def get_task_service(db: Session = Depends(get_db)):
    return TaskService(TaskRepository(db), BoardRepository(db), ProjectRepository(db))

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, svc: TaskService = Depends(get_task_service), user: User = Depends(get_current_user)):
    try:
        return svc.create_task(data, user)
    except (ValueError, PermissionError) as e:
        code = 404 if isinstance(e, ValueError) else 403
        raise HTTPException(status_code=code, detail=str(e))

@router.get("/board/{board_id}", response_model=PaginatedTaskResponse)
def get_board_tasks(
    board_id: int, 
    status: Optional[str] = Query(None, description="Filter tasks by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    svc: TaskService = Depends(get_task_service), 
    user: User = Depends(get_current_user)
):
    try:
        return svc.get_board_tasks(board_id, user, status, page, page_size)
    except (ValueError, PermissionError) as e:
        code = 404 if isinstance(e, ValueError) else 403
        raise HTTPException(status_code=code, detail=str(e))

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, svc: TaskService = Depends(get_task_service), user: User = Depends(get_current_user)):
    try:
        return svc.update_task(task_id, data, user)
    except (ValueError, PermissionError) as e:
        code = 404 if isinstance(e, ValueError) else 403
        raise HTTPException(status_code=code, detail=str(e))

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, svc: TaskService = Depends(get_task_service), user: User = Depends(get_current_user)):
    try:
        svc.delete_task(task_id, user)
    except (ValueError, PermissionError) as e:
        code = 404 if isinstance(e, ValueError) else 403
        raise HTTPException(status_code=code, detail=str(e))
