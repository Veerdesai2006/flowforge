from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.jwt_handler import verify_token
from app.db.database import get_db
from app.repositories.user import UserRepository
from app.models.user import UserRole


# =====================================================
# HTTP Bearer Security
# =====================================================

security = HTTPBearer()


# =====================================================
# Get Current User
# =====================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    # FastAPI calls get_db() and injects the database
    # session into this function.
):
    """
    Get the currently authenticated user.

    Steps:

    1. Read the Authorization header through HTTPBearer.
    2. Extract the Bearer token.
    3. Verify the JWT.
    4. Extract the user ID.
    5. Find the user in the database.
    """

    # -------------------------------------------------
    # Step 1: Extract the actual JWT
    # -------------------------------------------------

    token = credentials.credentials

    """
    HTTPBearer reads the Authorization header for us.

    Example request header:

    Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

    credentials.scheme:
        "Bearer"

    credentials.credentials:
        "eyJhbGciOiJIUzI1NiIs..."

    We only need the actual JWT, so we use:

    credentials.credentials
    """

    # -------------------------------------------------
    # Step 1.5: Check if token is blocked (LOGOUT CHECK)
    # -------------------------------------------------
    from app.repositories.auth import AuthRepository
    auth_repo = AuthRepository(db)
    
    # If the repository says this token is in the blocklist, reject the user!
    if auth_repo.is_token_blocked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -------------------------------------------------
    # Step 2: Verify and decode the JWT
    # -------------------------------------------------

    try:
        payload = verify_token(token)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    """
    verify_token() checks the JWT signature and expiration.

    If the token is valid, payload may look like:

    {
        "sub": "1",
        "exp": 1789132721,
        "type": "access"
    }
    """

    # -------------------------------------------------
    # Step 3: Check token type
    # -------------------------------------------------

    if payload.get("type") != "access":
        """
        An access token is used to access protected endpoints.

        A refresh token is used to obtain a new access token.

        We should not allow a refresh token to directly
        access protected endpoints.
        """

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -------------------------------------------------
    # Step 4: Extract user ID
    # -------------------------------------------------

    user_id = payload.get("sub")

    """
    When creating the token, we used:

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    Therefore, "sub" contains the user's ID.

    Example:

    {
        "sub": "1"
    }

    If the token does not contain "sub", we cannot
    identify the user.
    """

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain a user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -------------------------------------------------
    # Step 5: Find user in database
    # -------------------------------------------------

    repository = UserRepository(db)

    """
    Here we create a repository object and pass the
    database session into it.

    Conceptually:

    Database session
          ↓
    UserRepository
          ↓
    Database operations
    """

    user = repository.get_by_id(int(user_id))

    # -------------------------------------------------
    # Step 6: Check whether user exists
    # -------------------------------------------------

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -------------------------------------------------
    # Step 7: Return authenticated user
    # -------------------------------------------------

    return user


# =====================================================
# Require Admin User
# =====================================================

# =====================================================
# Require Admin User
# =====================================================

def require_admin(
    current_user=Depends(get_current_user),
):
    """
    Allow access to ADMIN and SUPER_ADMIN users.

    Steps:

    1. Get the authenticated user.
    2. Check the user's role.
    3. Allow ADMIN users.
    4. Allow SUPER_ADMIN users.
    5. Reject normal USER accounts.
    6. Return the authenticated user.
    """

    # -------------------------------------------------
    # Step 1: Check the user's role
    # -------------------------------------------------

    # We use the actual Enum members (UserRole.ADMIN) 
    # instead of plain strings ("ADMIN") to prevent typos.
    allowed_roles = {UserRole.ADMIN, UserRole.SUPER_ADMIN}

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    # -------------------------------------------------
    # Step 2: Return the authenticated admin user
    # -------------------------------------------------

    return current_user
# =====================================================
# Require Super Admin User
# =====================================================

def require_super_admin(
    current_user=Depends(get_current_user),
):
    """
    Allow access only to SUPER_ADMIN users.

    Steps:

    1. Get the authenticated user.
    2. Check the user's role.
    3. Reject ADMIN users.
    4. Reject USER users.
    5. Allow only SUPER_ADMIN users.
    6. Return the authenticated user.
    """

    # -------------------------------------------------
    # Step 1: Check the user's role
    # -------------------------------------------------

    # We compare directly against the Enum member.
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )

    # -------------------------------------------------
    # Step 2: Return the authenticated super admin
    # -------------------------------------------------

    return current_user