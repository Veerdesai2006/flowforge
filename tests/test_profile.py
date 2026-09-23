import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import io

from app.main import app
from app.db.database import get_db
from app.db.base import Base
from app.models import *
from app.core.jwt_handler import create_access_token

# ---------------------------------------------------------
# Test Setup (In-Memory SQLite)
# ---------------------------------------------------------

from sqlalchemy.pool import StaticPool

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
def test_user(db):
    user = User(
        email="profile@test.com", 
        password="hashedpassword", 
        first_name="Test", 
        last_name="User", 
        is_active=True,
        avatar_url="/static/default.png"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add a second user to test duplicate emails
    user2 = User(
        email="other@test.com", 
        password="hashedpassword", 
        first_name="Other", 
        last_name="User", 
        is_active=True
    )
    db.add(user2)
    db.commit()
    
    return user

@pytest.fixture(scope="function")
def auth_headers(test_user):
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_1_get_current_profile(client, auth_headers):
    """Test 1: Get current profile"""
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "profile@test.com"
    assert data["first_name"] == "Test"

def test_2_update_own_profile(client, auth_headers):
    """Test 2: Update own profile"""
    payload = {"first_name": "Updated", "last_name": "Name"}
    res = client.patch("/api/users/me", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"

def test_3_update_email(client, auth_headers):
    """Test 3: Update email"""
    payload = {"email": "newemail@test.com"}
    res = client.patch("/api/users/me", json=payload, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "newemail@test.com"

def test_4_duplicate_email(client, auth_headers):
    """Test 4: Duplicate email"""
    payload = {"email": "other@test.com"} # Belongs to user2
    res = client.patch("/api/users/me", json=payload, headers=auth_headers)
    assert res.status_code == 409
    assert "Email already in use" in res.json()["detail"]

def test_5_unauthorized_profile_update(client):
    """Test 5: Unauthorized profile update"""
    res = client.patch("/api/users/me", json={"first_name": "Hacker"})
    assert res.status_code == 403 # Missing token -> 403 Forbidden

def test_6_profile_image_upload(client, auth_headers):
    """Test 6: Profile image upload"""
    file_content = b"fake image content"
    files = {"file": ("avatar.jpg", file_content, "image/jpeg")}
    res = client.post("/api/upload/avatar", files=files, headers=auth_headers)
    assert res.status_code == 200
    assert "avatar_url" in res.json()
    assert "/static/uploads/avatars/" in res.json()["avatar_url"]

def test_7_invalid_image_type(client, auth_headers):
    """Test 7: Invalid image type"""
    file_content = b"print('malicious script')"
    files = {"file": ("script.py", file_content, "text/x-python")}
    res = client.post("/api/upload/avatar", files=files, headers=auth_headers)
    assert res.status_code == 400
    assert "Only JPEG, PNG, WebP, and GIF" in res.json()["detail"]

def test_8_oversized_image(client, auth_headers):
    """Test 8: Oversized image"""
    # 6MB file
    file_content = b"0" * (6 * 1024 * 1024)
    files = {"file": ("big.jpg", file_content, "image/jpeg")}
    res = client.post("/api/upload/avatar", files=files, headers=auth_headers)
    assert res.status_code == 400
    assert "File size must be under 5MB" in res.json()["detail"]

def test_9_banner_upload(client, auth_headers):
    """Test 9: Banner upload"""
    file_content = b"fake banner content"
    files = {"file": ("banner.png", file_content, "image/png")}
    res = client.post("/api/upload/banner", files=files, headers=auth_headers)
    assert res.status_code == 200
    assert "banner_url" in res.json()
    assert "/static/uploads/banners/" in res.json()["banner_url"]

def test_10_authentication_failure(client):
    """Test 10: Authentication failure"""
    files = {"file": ("avatar.jpg", b"fake", "image/jpeg")}
    res = client.post("/api/upload/avatar", files=files, headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401
    assert "Could not validate credentials" in res.json()["detail"]
