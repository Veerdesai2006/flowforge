"""
=========================================================
FlowForge - Token Blocklist Model
=========================================================

This file defines the TokenBlocklist table.

When a user logs out, their JWT is saved here.
If anyone tries to use a token that exists in this table,
the system will reject it.
"""

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import BaseModel

class TokenBlocklist(BaseModel):
    
    __tablename__ = "token_blocklist"

    """
    The actual JWT string.
    
    Why index=True?
    Because on EVERY protected API call, we must search 
    this table to see if the token exists. 
    An index makes this search lightning fast.
    """
    token: Mapped[str] = mapped_column(
        String, 
        index=True, 
        nullable=False, 
        unique=True
    )

    """
    We store the time the token was blocked.
    
    Why?
    Because blocklists can grow infinitely large over time.
    Later on, we could write a background script that deletes 
    tokens from this table if they are older than 30 days, 
    because the JWT itself would have expired anyway.
    """
    blocked_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
