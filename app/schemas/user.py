"""
=========================================================
FlowForge - User Schemas
=========================================================

Pydantic Schemas define

✔ Request Validation

✔ Response Serialization

✔ API Documentation

These schemas DO NOT create database tables.

SQLAlchemy Models create database tables.

Pydantic Schemas validate incoming
and outgoing data.
"""

# =====================================================
# Imports
# =====================================================

from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


# =====================================================
# User Role Enum
# =====================================================

"""
Keeping the API schema enum separate from the database
enum avoids coupling the API layer to SQLAlchemy.

Later we'll map between them automatically.
"""


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    USER = "USER"


# =====================================================
# Base User Schema
# =====================================================

"""
Base schema contains fields that are shared
between multiple schemas.

Instead of repeating

first_name
last_name
email

we inherit from this class.
"""


class UserBase(BaseModel):

    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="User First Name",
    )

    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="User Last Name",
    )

    email: EmailStr


# =====================================================
# Register User
# =====================================================


class UserCreate(UserBase):

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User Password",
    )


# =====================================================
# Login User
# =====================================================


class UserLogin(BaseModel):

    email: EmailStr

    password: str


# =====================================================
# User Response
# =====================================================

"""
This schema is returned to clients.

Notice:

Password is NOT included.

Never expose passwords through APIs.
"""


class UserResponse(UserBase):

    id: int

    role: UserRole

    is_active: bool

    is_verified: bool

    avatar_url: str | None = None

    banner_url: str | None = None

    created_at: datetime

    updated_at: datetime

    # Allows Pydantic to read SQLAlchemy models directly.
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# JWT Token Response
# =====================================================


class Token(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str = "bearer"


# =====================================================
# JWT Payload
# =====================================================

"""
Represents the data stored inside
a decoded JWT.

Example

{
    "sub": "veer@gmail.com",
    "role": "ADMIN",
    "exp": 1789034822
}
"""


class TokenPayload(BaseModel):

    sub: str

    role: UserRole

    exp: int


# =====================================================
# Update User (PATCH)
# =====================================================

class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    
    Notice that we use `| None = None`. 
    This means the fields are completely OPTIONAL.
    An admin can send just the role, just the status, or both.
    """
    role: UserRole | None = None
    is_active: bool | None = None

# =====================================================
# Update Profile (PATCH /me)
# =====================================================

class UserUpdateProfile(BaseModel):
    """
    Schema for a user updating their own profile.
    
    Users can only edit basic information. 
    They CANNOT edit their role or active status.
    """
    first_name: str | None = Field(None, min_length=2, max_length=50)
    last_name: str | None = Field(None, min_length=2, max_length=50)
    email: EmailStr | None = None