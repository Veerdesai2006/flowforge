import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.db.database import get_db
from app.models.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.board import Board
from app.models.task import Task
from app.core.security import create_access_token

# ---------------------------------------------------------
# Test Setup (In-Memory SQLite)
# ---------------------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Overide get_db in FastAPI app
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    yield db
    
    # Teardown
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    return TestClient(app)

@pytest.fixture(scope="function")
def auth_headers(db):
    # Create test user
    user = User(email="test@test.com", password="hashedpassword", first_name="Test", last_name="User", is_active=True)
    db.add(user)
    db.commit()
    token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}, user

@pytest.fixture(scope="function")
def setup_board(db, auth_headers):
    headers, user = auth_headers
    
    # Create Project and Board for pagination tests
    project = Project(name="Test Project", owner_id=user.id)
    db.add(project)
    db.commit()
    
    board = Board(name="Test Board", project_id=project.id)
    db.add(board)
    db.commit()
    
    # Create 87 tasks for TODO status (testing total_items = 87)
    tasks = []
    for i in range(87):
        tasks.append(Task(
            title=f"Task {i+1}",
            board_id=board.id,
            status="TODO",
            priority="MEDIUM",
            updated_at=datetime.utcnow() # Ensure deterministic ordering
        ))
    db.add_all(tasks)
    db.commit()
    
    return board.id, headers, user.id


# ---------------------------------------------------------
# Pagination Tests
# ---------------------------------------------------------

def test_1_first_page(client, setup_board):
    """Test: First page."""
    board_id, headers, _ = setup_board
    # page_size=10 by default
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO&page=1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert len(data["items"]) == 10
    
def test_2_second_page(client, setup_board):
    """Test: Second page."""
    board_id, headers, _ = setup_board
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO&page=2", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 2
    assert len(data["items"]) == 10

def test_3_last_page(client, setup_board):
    """Test: Last page."""
    board_id, headers, _ = setup_board
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO&page=9", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 9
    assert len(data["items"]) == 7 # 87 total items -> page 9 has 7 items

def test_4_page_beyond_total(client, setup_board):
    """Test: Page beyond total pages."""
    board_id, headers, _ = setup_board
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO&page=10", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 0

def test_5_different_page_sizes(client, setup_board):
    """Test: Different page sizes."""
    board_id, headers, _ = setup_board
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO&page=1&page_size=30", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["page_size"] == 30
    assert len(data["items"]) == 30
    assert data["total_pages"] == 3 # 87/30 = 3 pages

def test_6_empty_board(client, auth_headers, db):
    """Test: Empty board."""
    headers, user = auth_headers
    project = Project(name="Empty Project", owner_id=user.id)
    db.add(project)
    db.commit()
    board = Board(name="Empty Board", project_id=project.id)
    db.add(board)
    db.commit()
    
    res = client.get(f"/api/tasks/board/{board.id}?status=TODO&page=1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_items"] == 0
    assert data["total_pages"] == 1
    assert len(data["items"]) == 0

def test_7_8_correct_totals(client, setup_board):
    """Test: Correct total_items and correct total_pages."""
    board_id, headers, _ = setup_board
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO", headers=headers)
    data = res.json()
    assert data["total_items"] == 87
    assert data["total_pages"] == 9

def test_9_unauthorized_user(client, setup_board):
    """Test: Unauthorized user."""
    board_id, _, _ = setup_board
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO")
    assert res.status_code == 401

def test_10_access_another_user_board(client, setup_board, db):
    """Test: User accessing another user's board."""
    board_id, _, _ = setup_board
    
    # Create a SECOND user and try to access the first user's board
    user2 = User(email="hacker@test.com", password="hashedpassword", first_name="Hacker", last_name="User", is_active=True)
    db.add(user2)
    db.commit()
    token = create_access_token(data={"sub": str(user2.id)})
    headers2 = {"Authorization": f"Bearer {token}"}
    
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO", headers=headers2)
    assert res.status_code == 403

def test_11_task_creation(client, setup_board):
    """Test: Task creation."""
    board_id, headers, _ = setup_board
    payload = {"title": "New Pagination Task", "board_id": board_id, "priority": "HIGH"}
    res = client.post("/api/tasks", json=payload, headers=headers)
    assert res.status_code == 201
    
    # Verify total_items went from 87 to 88
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO", headers=headers)
    assert res.json()["total_items"] == 88

def test_12_task_deletion(client, setup_board, db):
    """Test: Task deletion."""
    board_id, headers, _ = setup_board
    
    # Grab the first task id
    task = db.query(Task).filter(Task.board_id == board_id).first()
    
    res = client.delete(f"/api/tasks/{task.id}", headers=headers)
    assert res.status_code == 204
    
    # Verify total_items went from 87 to 86
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO", headers=headers)
    assert res.json()["total_items"] == 86

def test_13_task_status_update(client, setup_board, db):
    """Test: Task status update."""
    board_id, headers, _ = setup_board
    
    task = db.query(Task).filter(Task.board_id == board_id, Task.status == "TODO").first()
    
    # Move from TODO to IN_PROGRESS
    res = client.patch(f"/api/tasks/{task.id}", json={"status": "IN_PROGRESS"}, headers=headers)
    assert res.status_code == 200
    
    # Verify TODO count dropped to 86
    res = client.get(f"/api/tasks/board/{board_id}?status=TODO", headers=headers)
    assert res.json()["total_items"] == 86
    
    # Verify IN_PROGRESS count is 1
    res = client.get(f"/api/tasks/board/{board_id}?status=IN_PROGRESS", headers=headers)
    assert res.json()["total_items"] == 1
