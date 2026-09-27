from pydantic import BaseModel
from typing import Optional, List, Any

class RegisterIn(BaseModel):
    username: str
    password: str
    role: str
    department: Optional[str] = None
    zone: Optional[str] = None

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str

class TaskIn(BaseModel):
    title: str
    km: float
    priority: str
    department: str
    duration_min: int
    overdue_days: int = 0

class TaskOut(TaskIn):
    id: int
    status: str
    setup_min: int
    safety_min: int
    clearance_min: int
    risk_score: Optional[int] = None
    risk_reasons: Optional[List[str]] = None

    class Config:
        from_attributes = True

class FeasibilityRequest(BaseModel):
    anchor_task_id: int
    start_time: Optional[str] = None

class RecommendationDecision(BaseModel):
    note: Optional[str] = None
