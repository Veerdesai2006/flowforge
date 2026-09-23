"""
=========================================================
FlowForge - Users API
=========================================================

This router handles User Management endpoints.
(Viewing users, changing roles, deactivating users).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.user import UserRepository
from app.services.user import UserService
from app.core.dependencies import require_admin, require_super_admin, get_current_user
from app.schemas.user import UserResponse, UserUpdate, UserUpdateProfile
from app.models.user import User

# ======================================================
# Router Setup
# ======================================================

router = APIRouter(
    prefix="/api/users",
    tags=["Users Management"],
)

# ======================================================
# Update Own Profile
# ======================================================

@router.patch("/me", response_model=UserResponse)
def update_me(
    update_data: UserUpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the authenticated user's own profile.
    """
    repository = UserRepository(db)
    service = UserService(repository)
    
    try:
        updated_user = service.update_profile(current_user, update_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT if "Email" in str(e) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ======================================================
# Get All Users
# ======================================================

@router.get("", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    # By adding require_admin here, FastAPI will automatically
    # block anyone who is not an ADMIN or SUPER_ADMIN.
    current_admin = Depends(require_admin)
):
    """
    Retrieve a list of all registered users.
    Only accessible by administrators.
    """
    
    # 1. Initialize our layers
    repository = UserRepository(db)
    service = UserService(repository)
    
    # 2. Ask the service to get all users
    users = service.get_all_users()
    
    # 3. Return the list (FastAPI automatically validates it against UserResponse)
    return users

# ======================================================
# Get User By ID
# ======================================================

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,  # FastAPI extracts {user_id} from the URL!
    db: Session = Depends(get_db),
    current_admin = Depends(require_admin)
):
    """
    Retrieve a specific user by their ID.
    Only accessible by administrators.
    """
    repository = UserRepository(db)
    service = UserService(repository)
    
    user = service.get_user_by_id(user_id)
    
    # If the database returns None, the user doesn't exist
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
        
    return user

# ======================================================
# Update User (Role / Status)
# ======================================================

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    # Allow ADMINs to use this endpoint, but enforce limits in the service!
    current_admin: User = Depends(require_admin)
):
    """
    Update a user's role or active status.
    Access is restricted by RBAC rules in the service layer.
    """
    repository = UserRepository(db)
    service = UserService(repository)
    
    try:
        updated_user = service.update_user(user_id, update_data, current_admin)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
