from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.core.db import SessionLocal
from app.models.ride import Ride
from app.models.user import User
from app.models.payment import Payment
from dependencies.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/driver/{driver_id}/earnings")
def get_driver_earnings(driver_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if not current_user.is_driver :
        raise HTTPException(status_code=403, detail="Unauthorized access to driver rides.")
    if current_user.is_driver and current_user.id != driver_id:
        raise HTTPException(status_code=403, detail="Drivers can only access their own rides.")
    earnings = db.query(Payment).filter(Payment.recipient_id == driver_id, Payment.status == "paid").all()
    total_earnings = sum(payment.amount for payment in earnings)
    return {
        "driver_id": driver_id,
        "total_earnings": total_earnings,
        "payments": earnings
    }
