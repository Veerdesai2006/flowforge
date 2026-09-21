"""
=========================================================
FlowForge - JWT Handler
=========================================================

This file is responsible for:

1. Creating Access Tokens
2. Creating Refresh Tokens
3. Verifying JWT Tokens
4. Decoding Token Payload

JWT = JSON Web Token

A JWT allows the client to authenticate
without sending the username/password
on every request.

Flow

Login
   │
   ▼
Generate JWT
   │
   ▼
Client stores JWT
   │
   ▼
Client sends JWT in Authorization Header
   │
   ▼
Backend verifies JWT
   │
   ▼
User is authenticated
"""

# =====================================================
# Imports
# =====================================================

from datetime import datetime, timedelta, timezone
#datetime - Give me the current date and time.
#timedelta - timedelta represents a duration.
"""timezone - We use:
timezone.utc
This means UTC timezone.
Your server may be running in India, the US, or another country. Using UTC gives us a consistent time reference.
"""
from typing import Any
"""This is used for type hints.
Look at:
data: dict[str, Any]
It means:data must be a dictionary whose keys are strings, and whose values can be of different types.
So Any gives flexibility to the dictionary values.
"""
from jose import JWTError, jwt
"""JWTError
from jose import JWTError
This is an exception provided by python-jose.
It is used when JWT-related errors occur.
For example:
- Invalid token
- Malformed token
- Invalid signature
- Some decoding-related problems
Important: In your current code, you import JWTError, but you are not using it yet.
We will discuss that when we reach the verification function."""

"""jwt
from jose import jwt
This is the main JWT functionality from python-jose.
You use:
jwt.encode()
to create a token.
And:
jwt.decode()
to decode and verify a token.
Think of it as the tool that performs the actual JWT work."""

from app.config.settings import settings
"""This imports your application's configuration object.
It probably contains values such as:
settings.secret_key
settings.algorithm
settings.access_token_expire_minutes"""

# =====================================================
# Create Access Token
# =====================================================


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT Access Token.

    Parameters
    ----------
    data : dict
        Payload to include in the token.

        Example

        {
            "sub": "veer@gmail.com",
            "role": "ADMIN"
        }

    expires_delta : timedelta | None

        Custom expiration time.

        If not provided,

        ACCESS_TOKEN_EXPIRE_MINUTES
        from settings.py will be used.

    Returns
    -------
    str

        Encoded JWT Token
    """

    # Create a copy so we don't modify
    # the original dictionary.
    payload = data.copy()

    # Determine expiration time.
    if expires_delta:

        expire = datetime.now(timezone.utc) + expires_delta
#If we give the time to expire then use that if we dont give then use else function
    else:

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    """Get the current UTC time
   datetime.now(timezone.utc)
   Suppose the current UTC time is:
   2026-09-11 06:30:00 UTC
   This is just an example.
   Get the configured expiration duration
   settings.access_token_expire_minutes
   Suppose your settings contain:
   access_token_expire_minutes = 30
   Then:
       timedelta(
        minutes=settings.access_token_expire_minutes
     )
    becomes:
    timedelta(minutes=30)
    That means:
    Add 30 minutes.

    7.3 Add the duration to the current time
    Conceptually:
    expire = current_utc_time + 30_minutes
    So:
    Current time:  06:30 UTC
    Duration:      30 minutes
                     │
                     ▼
    Expiration:    07:00 UTC
    The final value of expire is a datetime object."""

    # exp is a reserved JWT claim.
     #This adds an expiration time to the token.
    payload["exp"] = expire 

    # Optional token type
    #This adds a custom claim to identify what kind of token it is.
    payload["type"] = "access"


    # Encode JWT
    encoded_jwt = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt


# =====================================================
# Create Refresh Token
# =====================================================


def create_refresh_token(
    data: dict[str, Any],
) -> str:
    """
    Create Refresh Token.

    Refresh Tokens have a much longer life
    than Access Tokens.

    Example

    Access Token

        30 Minutes

    Refresh Token

        7 Days
    """

    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    payload["exp"] = expire
    #This adds an expiration time to the token.
    payload["type"] = "refresh"
    #This adds a custom claim to identify what kind of token it is.


    encoded_jwt = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt


# =====================================================
# Verify Token
# =====================================================


def verify_token(
    token: str,
) -> dict[str, Any]:
    """
    Verify JWT Token.

    If the token is

    ✔ Valid

    Returns

        Payload Dictionary

    Otherwise

        Raises JWTError
    """

    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    return payload


# =====================================================
# Decode Token Safely
# =====================================================


def decode_token(
    token: str,
) -> dict[str, Any] | None:
    """
    Decode JWT Token safely.

    Returns

    Payload

    OR

    None if token is invalid.

    Useful when we don't want the
    application to crash because
    of an invalid token.
    """

    try:

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        return payload

    except JWTError:

        return None