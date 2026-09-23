from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.board import BoardRepository
from app.repositories.project import ProjectRepository
from app.services.board import BoardService
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse

router = APIRouter(prefix="/api/boards", tags=["Boards"])

def get_board_service(db: Session = Depends(get_db)):
    return BoardService(BoardRepository(db), ProjectRepository(db))

@router.post("", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(
    board_data: BoardCreate,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    try:
        return service.create_board(board_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("/project/{project_id}", response_model=List[BoardResponse])
def get_project_boards(
    project_id: int,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    try:
        return service.get_project_boards(project_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("/{board_id}", response_model=BoardResponse)
def get_board(
    board_id: int,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    try:
        return service.get_board_by_id(board_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.patch("/{board_id}", response_model=BoardResponse)
def update_board(
    board_id: int,
    board_data: BoardUpdate,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    try:
        return service.update_board(board_id, board_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    board_id: int,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user)
):
    try:
        service.delete_board(board_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
