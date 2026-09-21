"""
=========================================================
FlowForge - Database Configuration
=========================================================

WHY THIS FILE EXISTS
--------------------

FastAPI needs a way to communicate with PostgreSQL.

SQLAlchemy does NOT connect automatically.

This file is responsible for:

✔ Creating the database engine
✔ Creating database sessions
✔ Providing sessions to FastAPI
✔ Managing connection pooling

Every database operation in the project will eventually
go through this file.

Architecture

FastAPI

↓

Session

↓

Engine

↓

PostgreSQL
"""

# =====================================================
# SQLAlchemy Imports
# =====================================================

# create_engine creates the connection pool to PostgreSQL.
from sqlalchemy import create_engine

# sessionmaker creates Session objects that talk to the DB.
from sqlalchemy.orm import sessionmaker

# Import our application settings.
from app.config.settings import settings


# =====================================================
# DATABASE URL
# =====================================================

"""
Remember,

settings.database_url automatically builds:

postgresql+psycopg2://user:password@host:port/database

using values from .env.
"""

DATABASE_URL = settings.database_url


# =====================================================
# SQLAlchemy Engine
# =====================================================

"""
Engine

Think of the engine as the "manager" of all database
connections.

It DOES NOT execute queries itself.

Instead, it creates and manages connections for Sessions.
"""

engine = create_engine(

    # PostgreSQL connection string
    DATABASE_URL,

    # Reuse existing database connections.
    # This avoids creating a new connection every request.
    pool_pre_ping=True,

    # Print SQL queries in terminal.
    # Keep False in production.
    echo=settings.debug,
)


# =====================================================
# Session Factory
# =====================================================

"""
sessionmaker()

Creates Session objects.

Every API request should receive its own Session.

Why?

Because multiple users can access the application
simultaneously.

Each request gets an isolated database transaction.
"""

SessionLocal = sessionmaker(

    # Bind every session to our engine.
    bind=engine,

    # Don't automatically commit changes.
    autocommit=False,

    # Don't automatically rollback transactions.
    autoflush=False,

    # Prevent SQLAlchemy from expiring objects
    # immediately after commit.
    #
    # Without this,
    #
    # user.name
    #
    # after commit may trigger another query.
    expire_on_commit=False,
)


# =====================================================
# Database Dependency
# =====================================================

"""
This function will be used inside FastAPI routes.

Example

def create_user(
    db: Session = Depends(get_db)
):

FastAPI automatically:

1. Creates a Session
2. Gives it to the route
3. Closes it after the request ends

This prevents database connection leaks.
"""


def get_db():
    """
    Generator function.

    yield returns the Session.

    finally always executes,

    even if an exception occurs.
    """

    db = SessionLocal()

    try:

        yield db

    finally:

        # VERY IMPORTANT

        # Always close the connection.

        db.close()