"""
=========================================================
FlowForge - Password Security
=========================================================

This file is responsible for password security.

We NEVER store plain-text passwords in the database.

Instead, we:

User Password
      │
      ▼
Hash Password
      │
      ▼
Store Hash in Database

During login:

Entered Password
        │
        ▼
Compare With Stored Hash

If matched

Login Success

Otherwise

Login Failed
"""

# =====================================================
# Imports
# =====================================================

from passlib.context import CryptContext

# =====================================================
# Password Hashing Configuration
# =====================================================

"""
CryptContext

Passlib provides many hashing algorithms.

Examples

bcrypt
argon2
pbkdf2_sha256
sha256_crypt

We choose bcrypt because

✔ Widely used

✔ Secure

✔ Automatically generates salt

✔ Recommended for authentication

What is CryptContext?
Instead of directly calling bcrypt everywhere:
bcrypt.hashpw(...)
Passlib wraps hashing algorithms in a single interface.
Benefits:
- Easier to switch algorithms later.
- Handles algorithm metadata automatically.
- Cleaner code.

What does deprecated="auto" mean?
Suppose today we use:
bcrypt
Five years later we migrate to:
argon2
Old users still have bcrypt hashes.
When they log in:
- Passlib recognizes the old algorithm.
- Verifies the password.
- Can automatically upgrade the hash on the next login if configured.
This makes future migrations much easier.
"""

pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto",
)

# =====================================================
# Hash Password
# =====================================================


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into
    a secure bcrypt hash.

    Example

    Input

    Password@123

    Output

    $2b$12$2VE......

    Returns
    -------
    str
        Hashed password
    """

    return pwd_context.hash(password)


# =====================================================
# Verify Password
# =====================================================


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Compare

    User Entered Password

    with

    Stored Database Hash

    Returns

    True

    if matched

    otherwise False
    """

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )