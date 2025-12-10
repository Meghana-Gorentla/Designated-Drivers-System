# app/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from dependencies.auth import get_current_user
from app.schemas.user import UserOut # Import your UserOut schema
from app.models.user import User # Import your User model

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=UserOut)
def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's details.
    """
    return current_user