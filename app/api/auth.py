"""
=========================================================
FlowForge - Authentication API
=========================================================

This router handles all authentication-related endpoints.

Responsibilities

✓ Register User
✓ Login User
✓ Refresh Token 
✓ Logout (Later)
"""

# ======================================================
# Imports
# ======================================================

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException, status, Form
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.services.user import UserService
from app.core.security import verify_password
from app.core.dependencies import get_current_user,require_admin,require_super_admin,security
from app.core.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
)

from app.schemas.auth import (
    RegisterResponse,
    LoginResponse,
    UserResponse,
    RefreshTokenRequest
) 
from jose import JWTError

# ======================================================
# Router
# ======================================================

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

# ======================================================
# Register User
# ======================================================

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    #FastAPI runs get_db.
    # A new database session is created and yielded.
    #The register function runs, receiving that session as the db variable.
    #You can use db to query or save data (e.g., db.add(user)).
    #Once register finishes, the finally block in get_db runs, closing the connection automatically.
):
    """
    Register a new user.

    Request Body

    {
        "first_name": "...",
        "last_name": "...",
        "email": "...",
        "password": "..."
    }
    """

    repository = UserRepository(db)
    """Purpose: The Repository is responsible for database operations only (CRUD). 
    It knows how to talk to SQLAlchemy but doesn't know about business rules.
Why pass db?: The repository needs an active database session to execute queries like db.query(User).filter(...)."""

    service = UserService(repository)
    """Purpose: The Service contains business logic. It orchestrates what happens when a user registers (e.g., "check if email exists," "hash password," "send welcome email").
Why pass repository?: The service doesn't touch the database directly. It asks the repository to do the heavy lifting. This keeps the service testable without a real database.
Benefit: You can unit-test UserService by passing a fake/mock repository. You don't need a running DB to test if your validation logic works."""

    try:

        created_user = service.create_user(user)
        return RegisterResponse(
    message="User registered successfully.",
    user=UserResponse.model_validate(created_user),
)



    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
# ======================================================
# Login User
# ======================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    username: str = Form(default=None),
    password: str = Form(default=None),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user via form data (for Jinja2 frontend)
    or query params (for Swagger testing).
    """

    repository = UserRepository(db)
    service = UserService(repository)

    user = service.get_user_by_email(username)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated.")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


# ======================================================
# Refresh Access Token
# ======================================================

@router.post("/refresh")
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a new access token using a valid refresh token.

    Steps:

    1. Receive the refresh token.
    2. Verify the JWT signature and expiration.
    3. Check that the token is a refresh token.
    4. Extract the user ID.
    5. Check that the user still exists.
    6. Generate a new access token.
    7. Return the new access token.
    """

    # -----------------------------------------
    # Verify the refresh token
    # -------------------------
    try:
        payload = verify_token(request.refresh_token)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -----------------------------------------
    # Check token type
    # -----------------------------------------

    # Access tokens and refresh tokens are both JWTs.
    # The "type" field tells us which kind of token
    # the client has submitted.

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. A refresh token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -----------------------------------------
    # Extract user ID
    # -----------------------------------------

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token does not contain a user ID.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -----------------------------------------
    # Find the user
    # -----------------------------------------

    repository = UserRepository(db)

    user = repository.get_by_id(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token was not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -----------------------------------------
    # Generate a new access token
    # -----------------------------------------

    new_access_token = create_access_token(
        data={
            "sub": str(user.id),
        },
    )

    # -----------------------------------------
    # Return the new access token
    # -----------------------------------------

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
# =====================================================
# Get Current Authenticated User
# =====================================================

@router.get("/me", response_model=UserResponse)
#The endpoint should return data matching the UserResponse schema.
def get_me(
    current_user=Depends(get_current_user),
    #Before executing get_me(), FastAPI must execute get_current_user().
):
    """
    Return the currently authenticated user's details.

    The get_current_user dependency:

    1. Reads the Authorization header.
    2. Extracts the Bearer token.
    3. Verifies the JWT.
    4. Extracts the user ID.
    5. Finds the user in the database.
    6. Returns the user object.
    """

    return current_user
# =====================================================
# Admin Protected Test Endpoint
# =====================================================

@router.get("/admin-test")
def admin_test(current_user=Depends(require_admin)):
    #Before this endpoint runs, FastAPI must execute require_admin().
    #If the user is not an admin, the endpoint function will not run.
    """
    Test endpoint accessible only to ADMIN users.

    The require_admin dependency:

    1. Checks whether the JWT is valid.
    2. Finds the current user.
    3. Checks whether the user's role is ADMIN.
    4. Rejects normal users.
    """

    return {
        "message": "Welcome, Admin!",
        "user_id": current_user.id,
        "role": current_user.role,
    }
# =====================================================
# Super Admin Protected Test Endpoint
# =====================================================

@router.get("/super-admin-test")
def super_admin_test(
    current_user=Depends(require_super_admin),
):
    """
    Test endpoint accessible only to SUPER_ADMIN users.

    The require_super_admin dependency:

    1. Checks whether the JWT is valid.
    2. Finds the current user.
    3. Checks whether the user's role is SUPER_ADMIN.
    4. Rejects ADMIN and USER accounts.
    """

    return {
        "message": "Welcome, Super Admin!",
        "user_id": current_user.id,
        "role": current_user.role,
    }

# ======================================================
# Logout User
# ======================================================

@router.post("/logout")
def logout(
    # We require the user to be logged in to log out.
    # We also need the raw token string so we can block it.
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    # We also depend on get_current_user just to ensure the token is actually valid 
    # before we bother blocking it.
    current_user = Depends(get_current_user) 
):
    """
    Log out the user by adding their current access token 
    to the blocklist.
    """
    from app.repositories.auth import AuthRepository
    
    # Extract the raw JWT string
    token = credentials.credentials
    
    # Save it to the database blocklist
    auth_repo = AuthRepository(db)
    auth_repo.add_token_to_blocklist(token)

    return {"message": "Successfully logged out."}