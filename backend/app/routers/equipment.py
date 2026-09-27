from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/api", tags=["equipment"])

@router.get("/equipment")
def list_equipment(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    items = db.query(models.Equipment).all()
    return [
        {"id": e.id, "name": e.name, "type": e.type, "depot_id": e.depot_id,
         "depot_name": e.depot.name if e.depot else None,
         "travel_min": e.travel_min, "prep_min": e.prep_min, "status": e.status}
        for e in items
    ]

@router.get("/depots")
def list_depots(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    items = db.query(models.Depot).all()
    return [{"id": d.id, "name": d.name, "location": d.location} for d in items]
