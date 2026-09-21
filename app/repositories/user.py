"""
=========================================================
FlowForge - User Repository
=========================================================

The Repository layer is responsible ONLY for
database operations.

Responsibilities

✔ Insert data
✔ Update data
✔ Delete data
✔ Fetch data

It DOES NOT contain business logic.

Business logic belongs to the Service layer.
"""

# =====================================================
# Imports
# =====================================================

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Repository class for all database operations
    related to the User model.
    """

    def __init__(self, db: Session):
        """
        Store the SQLAlchemy database session.

        Every repository method will use this session
        to interact with the database.
        """
        self.db = db

    # ==================================================
    # Create User
    # ==================================================

    def create(self, user: User) -> User:
        """
        Save a new user into the database.

        Steps

        1. Add object to session
        2. Commit transaction
        3. Refresh object
        4. Return inserted user
        """

        self.db.add(user)

        self.db.commit()

        self.db.refresh(user)

        return user

    # ==================================================
    # Get User By Email
    # ==================================================

    def get_by_email(self, email: str) -> User | None:
        """
        Find a user using their email address.

        Returns

        User object

        OR

        None if user does not exist.
        """

        statement = select(User).where(User.email == email)

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    # ==================================================
    # Get User By ID
    # ==================================================

    def get_by_id(self, user_id: int) -> User | None:
        """
        Find a user using their primary key.
        """

        statement = select(User).where(User.id == user_id)

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    # ==================================================
    # Get All Users
    # ==================================================

    def get_all(self) -> list[User]:
        """
        Return all users from the database.
        """

        statement = select(User)

        result = self.db.execute(statement)

        return list(result.scalars().all())

    # ==================================================
    # Update User
    # ==================================================

    def update(self, user: User) -> User:
        """
        Commit changes made to an existing user.

        SQLAlchemy already tracks changes,
        so we only need to commit and refresh.
        """

        self.db.commit()

        self.db.refresh(user)

        return user

    # ==================================================
    # Delete User
    # ==================================================

    def delete(self, user: User) -> None:
        """
        Permanently delete a user.
        """

        self.db.delete(user)

        self.db.commit()