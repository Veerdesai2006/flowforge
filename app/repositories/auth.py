"""
=========================================================
FlowForge - Auth Repository
=========================================================

Handles database operations specifically related to 
authentication, like managing the token blocklist.
"""

from sqlalchemy.orm import Session
from app.models.token_blocklist import TokenBlocklist

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_token_to_blocklist(self, token: str) -> None:
        """
        Takes a JWT string and saves it into the blocklist table.
        """
        blocked_token = TokenBlocklist(token=token)
        self.db.add(blocked_token)
        self.db.commit()

    def is_token_blocked(self, token: str) -> bool:
        """
        Checks if a JWT string exists in the blocklist table.
        Returns True if it's blocked, False if it is clean.
        """
        # We query the blocklist table filtering by the token string.
        # .first() returns the record if found, or None if not found.
        record = self.db.query(TokenBlocklist).filter(
            TokenBlocklist.token == token
        ).first()
        
        return record is not None
