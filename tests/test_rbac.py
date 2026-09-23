import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db
from app.db.base import Base
from app.models import *
from app.models.user import UserRole
from app.core.jwt_handler import create_access_token

# ---------------------------------------------------------
# Test Setup (In-Memory SQLite)
# ---------------------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    return TestClient(app)

@pytest.fixture(scope="function")
def normal_user(db):
    user = User(
        email="normal@test.com", password="pwd", first_name="Normal", last_name="User", role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def admin_user(db):
    user = User(
        email="admin@test.com", password="pwd", first_name="Admin", last_name="User", role=UserRole.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def super_admin_user(db):
    user = User(
        email="super@test.com", password="pwd", first_name="Super", last_name="Admin", role=UserRole.SUPER_ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def normal_user_token(normal_user):
    return create_access_token(data={"sub": str(normal_user.id)})

@pytest.fixture(scope="function")
def admin_token(admin_user):
    return create_access_token(data={"sub": str(admin_user.id)})

@pytest.fixture(scope="function")
def super_admin_token(super_admin_user):
    return create_access_token(data={"sub": str(super_admin_user.id)})

# ---------------------------------------------------------
# Test Pytest RBAC & Dashboards
# ---------------------------------------------------------

def test_1_user_can_access_user_dashboard(client: TestClient, db: Session, normal_user_token: str):
    response = client.get("/api/dashboard/user", headers={"Authorization": f"Bearer {normal_user_token}"})
    assert response.status_code == 200
    assert "my_topics" in response.json()

def test_2_user_cannot_access_admin_dashboard(client: TestClient, db: Session, normal_user_token: str):
    response = client.get("/api/dashboard/admin", headers={"Authorization": f"Bearer {normal_user_token}"})
    assert response.status_code == 403

def test_3_user_cannot_access_super_admin_dashboard(client: TestClient, db: Session, normal_user_token: str):
    response = client.get("/api/dashboard/super-admin", headers={"Authorization": f"Bearer {normal_user_token}"})
    assert response.status_code == 403

def test_4_admin_can_access_admin_dashboard(client: TestClient, db: Session, admin_token: str):
    response = client.get("/api/dashboard/admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "total_users" in response.json()

def test_5_admin_cannot_access_super_admin_dashboard(client: TestClient, db: Session, admin_token: str):
    response = client.get("/api/dashboard/super-admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 403

def test_6_super_admin_can_access_all_dashboards(client: TestClient, db: Session, super_admin_token: str):
    response1 = client.get("/api/dashboard/super-admin", headers={"Authorization": f"Bearer {super_admin_token}"})
    assert response1.status_code == 200
    
    response2 = client.get("/api/dashboard/admin", headers={"Authorization": f"Bearer {super_admin_token}"})
    assert response2.status_code == 200

def test_7_admin_can_view_users(client: TestClient, db: Session, admin_token: str):
    response = client.get("/api/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

def test_8_admin_cannot_modify_super_admin(client: TestClient, db: Session, admin_token: str, super_admin_user: User):
    # Admin tries to deactivate Super Admin
    response = client.patch(
        f"/api/users/{super_admin_user.id}", 
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    assert "Admins cannot modify Super Admin" in response.json()["detail"]

def test_9_admin_cannot_promote_to_super_admin(client: TestClient, db: Session, admin_token: str, normal_user: User):
    # Admin tries to promote a regular user to Super Admin
    response = client.patch(
        f"/api/users/{normal_user.id}", 
        json={"role": "SUPER_ADMIN"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    assert "Admins cannot grant Super Admin privileges" in response.json()["detail"]

def test_10_super_admin_can_promote_roles(client: TestClient, db: Session, super_admin_token: str, normal_user: User):
    # Super Admin promotes a regular user to Admin
    response = client.patch(
        f"/api/users/{normal_user.id}", 
        json={"role": "ADMIN"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "ADMIN"
