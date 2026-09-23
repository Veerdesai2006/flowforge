"""
=========================================================
FlowForge - Dashboard Schemas
=========================================================
"""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ActivitySchema(BaseModel):
    id: int
    user_id: int
    action: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserDashboardResponse(BaseModel):
    my_topics: int
    my_boards: int
    my_tasks: int
    completed_tasks: int
    running_tasks: int
    postponed_tasks: int
    recent_activity: List[ActivitySchema]

class AdminDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    recent_users: int  # users joined recently
    permitted_activity: List[ActivitySchema]

class SuperAdminDashboardResponse(BaseModel):
    total_users: int
    total_admins: int
    total_super_admins: int
    active_users: int
    inactive_users: int
    recent_activity: List[ActivitySchema]
