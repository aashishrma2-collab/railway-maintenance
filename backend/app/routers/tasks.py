from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth, scoring
from ..database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

CAN_CREATE = ("Engineering", "S&T", "Electrical", "Planner", "Admin")

def _to_out(t: models.MaintenanceTask) -> dict:
    s = scoring.score_task(t)
    return {
        "id": t.id, "title": t.title, "km": t.km, "priority": t.priority,
        "department": t.department, "duration_min": t.duration_min,
        "setup_min": t.setup_min, "safety_min": t.safety_min, "clearance_min": t.clearance_min,
        "overdue_days": t.overdue_days, "status": t.status,
        "risk_score": s["score"], "risk_reasons": s["reasons"],
    }

@router.get("")
def list_tasks(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    tasks = db.query(models.MaintenanceTask).order_by(models.MaintenanceTask.id.desc()).all()
    return [_to_out(t) for t in tasks]

@router.post("")
def create_task(payload: schemas.TaskIn, db: Session = Depends(get_db),
                user: models.User = Depends(auth.require_roles(*CAN_CREATE))):
    t = models.MaintenanceTask(
        title=payload.title, km=payload.km, priority=payload.priority,
        department=payload.department, duration_min=payload.duration_min,
        overdue_days=payload.overdue_days, created_by=user.username,
    )
    db.add(t); db.commit(); db.refresh(t)
    return _to_out(t)

@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    t = db.query(models.MaintenanceTask).get(task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    return _to_out(t)
