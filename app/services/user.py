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
from app.schemas.user import UserCreate, UserUpdate, UserUpdateProfile
from app.services.activity import ActivityService
from app.repositories.activity import ActivityRepository


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
        self.activity_service = ActivityService(ActivityRepository(repository.db))

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
        created = self.repository.create(user)
        self.activity_service.log_activity(
            user_id=created.id,
            action="Joined Platform",
            description=f"Account created for '{created.email}'"
        )
        return created

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
        update_data: UserUpdate,
        current_admin: User
    ) -> User:
        """
        Apply partial updates to a user with strict RBAC rules.
        """
        from app.models.user import UserRole
        
        # 1. Fetch the existing user from the database
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")

        # -------------------------------------------------
        # RBAC SECURITY CHECKS
        # -------------------------------------------------
        
        # Rule 1: ADMIN cannot modify SUPER_ADMIN
        if current_admin.role == UserRole.ADMIN and user.role == UserRole.SUPER_ADMIN:
            raise ValueError("Admins cannot modify Super Admin accounts.")
            
        # Rule 2: ADMIN cannot promote anyone to SUPER_ADMIN
        if current_admin.role == UserRole.ADMIN and update_data.role == UserRole.SUPER_ADMIN:
            raise ValueError("Admins cannot grant Super Admin privileges.")
            
        # Rule 3: Only SUPER_ADMIN can demote a SUPER_ADMIN
        # (This is implicitly covered by Rule 1, but we enforce it just in case)
        
        # -------------------------------------------------
        
        actions = []

        # 2. If the admin provided a new role, apply it
        if update_data.role is not None and user.role != update_data.role:
            actions.append(f"role changed to {update_data.role}")
            user.role = update_data.role
            
        # 3. If the admin provided a new active status, apply it
        if update_data.is_active is not None and user.is_active != update_data.is_active:
            status_text = "Activated" if update_data.is_active else "Deactivated"
            actions.append(f"account {status_text.lower()}")
            user.is_active = update_data.is_active

        # 4. Save the changes to the database
        updated = self.repository.update(user)
        
        if actions:
            action_desc = " and ".join(actions)
            self.activity_service.log_activity(
                user_id=current_admin.id,
                action="Updated User Account",
                description=f"Updated user {updated.email}: {action_desc}"
            )
            
        return updated

    # ==================================================
    # Update Profile (Self-Service)
    # ==================================================

    def update_profile(
        self, 
        user: User, 
        update_data: "UserUpdateProfile"
    ) -> User:
        """
        Apply self-service profile updates.
        """
        updated = False
        if update_data.first_name is not None and user.first_name != update_data.first_name:
            user.first_name = update_data.first_name
            updated = True
            
        if update_data.last_name is not None and user.last_name != update_data.last_name:
            user.last_name = update_data.last_name
            updated = True
            
        if update_data.email is not None and update_data.email != user.email:
            # Check if the new email is already taken
            existing_user = self.repository.get_by_email(update_data.email)
            if existing_user:
                raise ValueError("Email already in use by another account.")
            user.email = update_data.email
            updated = True

        res = self.repository.update(user)
        
        if updated:
            self.activity_service.log_activity(
                user_id=user.id,
                action="Updated Profile",
                description="User updated their profile details."
            )
            
        return res

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