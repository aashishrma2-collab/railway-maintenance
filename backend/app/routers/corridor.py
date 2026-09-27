from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..feasibility import check_feasibility
from ..config import CORRIDOR_RADIUS_KM

router = APIRouter(prefix="/api/corridor", tags=["corridor"])
CAN_RUN = ("Planner", "Officer", "Admin")

def _get_config(db: Session) -> models.OpsConfig:
    cfg = db.query(models.OpsConfig).first()
    if not cfg:
        cfg = models.OpsConfig(id=1, block_window_min=180, maintenance_start="14:00")
        db.add(cfg); db.commit(); db.refresh(cfg)
    return cfg

def _equipment_for(db: Session, dept: str):
    return db.query(models.Equipment).filter(
        models.Equipment.type == dept, models.Equipment.status == "Available"
    ).first()

@router.post("/feasibility")
def run_feasibility(payload: schemas.FeasibilityRequest, db: Session = Depends(get_db),
                    user: models.User = Depends(auth.require_roles(*CAN_RUN))):
    anchor = db.query(models.MaintenanceTask).get(payload.anchor_task_id)
    if not anchor:
        raise HTTPException(404, "Anchor task not found")

    cfg = _get_config(db)
    start_time = payload.start_time or cfg.maintenance_start

    candidates = db.query(models.MaintenanceTask).filter(
        models.MaintenanceTask.id != anchor.id,
        models.MaintenanceTask.status == "Pending",
    ).all()
    corridor_candidates = [t for t in candidates if abs(t.km - anchor.km) <= CORRIDOR_RADIUS_KM]
    bundle = [anchor] + corridor_candidates

    results = []
    for t in bundle:
        eq = _equipment_for(db, t.department)
        results.append(check_feasibility(start_time, eq, t, cfg.block_window_min))

    feasible_task_ids = [r["task_id"] for r in results if r["feasible"]]

    rec = models.Recommendation(
        anchor_task_id=anchor.id, start_time=start_time,
        block_window_min=cfg.block_window_min, results=results, created_by=user.username,
    )
    db.add(rec); db.commit(); db.refresh(rec)

    return {
        "recommendation_id": rec.id,
        "anchor_task_id": anchor.id,
        "start_time": start_time,
        "block_window_min": cfg.block_window_min,
        "results": results,
        "feasible_task_ids": feasible_task_ids,
    }
