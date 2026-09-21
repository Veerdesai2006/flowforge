"""
=========================================================
FlowForge - User Service
=========================================================

The Service layer contains all business logic.

Responsibilities

✔ Validate business rules
✔ Call repository methods
✔ Hash passwords
✔ Raise business exceptions

The Service layer DOES NOT directly write SQL.
It communicates with the Repository layer.
"""

# =====================================================
# Imports
# =====================================================

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """
    Handles all business logic related to users.
    """

    def __init__(self, repository: UserRepository):
        """
        Inject the repository dependency.

        This keeps the service independent from
        SQLAlchemy implementation details.
        """
        self.repository = repository

    # ==================================================
    # Register User
    # ==================================================

    def create_user(
        self,
        user_data: UserCreate,
    ) -> User:
        """
        Register a new user.

        Business Rules

        1. Email must be unique.
        2. Password should be hashed.
        3. Save user to database.
        """

        # ---------------------------------------------
        # Check if email already exists
        # ---------------------------------------------
        existing_user = self.repository.get_by_email(
            user_data.email
        )

        if existing_user:
            raise ValueError("Email already registered.")

        # ---------------------------------------------
        # Create SQLAlchemy model
        # ---------------------------------------------
        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,

            # Never store plain-text passwords
            password=hash_password(user_data.password),
        )

        # ---------------------------------------------
        # Save to database
        # ---------------------------------------------
        return self.repository.create(user)

    # ==================================================
    # Get User By Email
    # ==================================================

    def get_user_by_email(
        self,
        email: str,
    ) -> User | None:
        """
        Find a user by email.
        """

        return self.repository.get_by_email(email)

    # ==================================================
    # Get User By ID
    # ==================================================

    def get_user_by_id(
        self,
        user_id: int,
    ) -> User | None:
        """
        Find a user by ID.
        """

        return self.repository.get_by_id(user_id)

    # ==================================================
    # Get All Users
    # ==================================================

    def get_all_users(
        self,
    ) -> list[User]:
        """
        Return all users.
        """

        return self.repository.get_all()

    # ==================================================
    # Update User
    # ==================================================

    def update_user(
        self, 
        user_id: int, 
        update_data: UserUpdate
    ) -> User:
        """
        Apply partial updates to a user.
        """
        
        # 1. Fetch the existing user from the database
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")

        # 2. If the admin provided a new role, apply it
        if update_data.role is not None:
            user.role = update_data.role
            
        # 3. If the admin provided a new active status, apply it
        if update_data.is_active is not None:
            user.is_active = update_data.is_active

        # 4. Save the changes to the database
        return self.repository.update(user)

    # ==================================================
    # Delete User
    # ==================================================

    def delete_user(
        self,
        user: User,
    ) -> None:
        """
        Delete a user.
        """

        self.repository.delete(user)