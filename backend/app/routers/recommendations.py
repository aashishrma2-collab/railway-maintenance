from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])
CAN_DECIDE = ("Planner", "Officer", "Admin")

def _to_out(r: models.Recommendation) -> dict:
    return {
        "id": r.id, "anchor_task_id": r.anchor_task_id, "start_time": r.start_time,
        "block_window_min": r.block_window_min, "status": r.status, "results": r.results,
        "created_by": r.created_by, "created_at": r.created_at.isoformat() if r.created_at else None,
        "decided_by": r.decided_by,
    }

@router.get("")
def list_recs(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    recs = db.query(models.Recommendation).order_by(models.Recommendation.id.desc()).all()
    return [_to_out(r) for r in recs]

@router.post("/{rec_id}/approve")
def approve(rec_id: int, payload: schemas.RecommendationDecision, db: Session = Depends(get_db),
           user: models.User = Depends(auth.require_roles(*CAN_DECIDE))):
    r = db.query(models.Recommendation).get(rec_id)
    if not r:
        raise HTTPException(404, "Recommendation not found")
    r.status = "Approved"
    r.decided_by = user.username
    r.decided_at = datetime.utcnow()
    db.commit()
    return _to_out(r)

@router.post("/{rec_id}/reject")
def reject(rec_id: int, payload: schemas.RecommendationDecision, db: Session = Depends(get_db),
          user: models.User = Depends(auth.require_roles(*CAN_DECIDE))):
    r = db.query(models.Recommendation).get(rec_id)
    if not r:
        raise HTTPException(404, "Recommendation not found")
    r.status = "Rejected"
    r.decided_by = user.username
    r.decided_at = datetime.utcnow()
    db.commit()
    return _to_out(r)
