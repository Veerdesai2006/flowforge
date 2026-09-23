"""
=========================================================
FlowForge - Project Schemas
=========================================================
Validates incoming data for creating/updating projects,
and formats outgoing data.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# =====================================================
# Base Schema (Shared Fields)
# =====================================================

class ProjectBase(BaseModel):
    name: str = Field(
        ..., # The three dots mean this field is REQUIRED
        min_length=2, 
        max_length=100,
        description="Project Name"
    )
    
    # Description is optional (can be None)
    description: str | None = Field(default=None, max_length=500)

# =====================================================
# Create Schema
# =====================================================

class ProjectCreate(ProjectBase):
    # Creating a project just needs a name and description, 
    # so we just inherit from ProjectBase!
    pass

# =====================================================
# Update Schema (PATCH)
# =====================================================

class ProjectUpdate(BaseModel):
    # Everything is optional because the user might just
    # want to update the description but leave the name alone.
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)

# =====================================================
# Response Schema
# =====================================================

class ProjectResponse(ProjectBase):
    """
    This is what the API sends back to the user.
    """
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    # Allows Pydantic to read SQLAlchemy models directly
    model_config = ConfigDict(from_attributes=True)
