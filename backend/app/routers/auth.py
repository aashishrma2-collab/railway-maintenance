from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

VALID_ROLES = {"Engineering", "S&T", "Electrical", "Operations", "Planner", "Officer", "Admin"}

@router.post("/register", response_model=schemas.TokenOut)
def register(payload: schemas.RegisterIn, db: Session = Depends(get_db)):
    if payload.role not in VALID_ROLES:
        raise HTTPException(400, f"Invalid role. Must be one of {sorted(VALID_ROLES)}")
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(400, "Username already exists")
    user = models.User(
        username=payload.username,
        password_hash=auth.hash_password(payload.password),
        role=payload.role,
        department=payload.department,
        zone=payload.zone,
    )
    db.add(user)
    db.commit()
    token = auth.create_token(user.username, user.role)
    return schemas.TokenOut(access_token=token, role=user.role, username=user.username)

@router.post("/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Incorrect username or password")
    token = auth.create_token(user.username, user.role)
    return schemas.TokenOut(access_token=token, role=user.role, username=user.username)

@router.get("/me")
def me(user: models.User = Depends(auth.get_current_user)):
    return {"username": user.username, "role": user.role, "department": user.department, "zone": user.zone}
