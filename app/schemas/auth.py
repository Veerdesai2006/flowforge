"""
=========================================================
FlowForge - Authentication Schemas
=========================================================

These schemas define the request and response
structures used by authentication APIs.
"""

from pydantic import BaseModel, ConfigDict

class RefreshTokenRequest(BaseModel):
    """
    Request body used when a client wants to
    generate a new access token.
    """

    refresh_token: str


# ======================================================
# User Response
# ======================================================

class UserResponse(BaseModel):
    """
    Public user information.

    We never expose sensitive fields like password.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    first_name: str

    last_name: str

    email: str

    role: str


# ======================================================
# Register Response
# ======================================================

class RegisterResponse(BaseModel):
    """
    Response returned after successful registration.
    """

    message: str

    user: UserResponse


# ======================================================
# Login Response
# ======================================================

class LoginResponse(BaseModel):
    """
    Response returned after successful login.
    """

    access_token: str

    refresh_token: str

    token_type: str = "bearer"

    user: UserResponse