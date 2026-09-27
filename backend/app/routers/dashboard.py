from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    tasks = db.query(models.MaintenanceTask).all()
    equipment = db.query(models.Equipment).all()
    recs = db.query(models.Recommendation).all()
    return {
        "total_tasks": len(tasks),
        "high_priority": sum(1 for t in tasks if t.priority == "High"),
        "overdue": sum(1 for t in tasks if (t.overdue_days or 0) > 0),
        "equipment_available": sum(1 for e in equipment if e.status == "Available"),
        "pending_approval": sum(1 for r in recs if r.status == "Pending Approval"),
        "approved": sum(1 for r in recs if r.status == "Approved"),
        "rejected": sum(1 for r in recs if r.status == "Rejected"),
    }
