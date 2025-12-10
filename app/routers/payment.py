from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.dependencies import models
from sqlalchemy.orm import Session


from app.models.payment import Payment
from app.models.ride import Ride
from app.models.user import User
from app.core.db import SessionLocal
from pydantic import BaseModel
from dependencies.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PaymentCreate(BaseModel):
    ride_id: int
    method: str  # e.g., cash, UPI, card

@router.post("/make_payment")
def make_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Check if ride exists and is completed
    ride = db.query(Ride).filter(Ride.id == data.ride_id).first()
    if not ride or ride.status != "completed":
        raise HTTPException(status_code=400, detail="Payment can only be made after ride completion.")

    # 2. Authorization check
    if ride.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to make payment for this ride.")

    # 3. Look for existing pending payment
    existing_payment = db.query(Payment).filter(
        Payment.ride_id == data.ride_id
    ).first()

    if not existing_payment:
        raise HTTPException(status_code=400, detail="No pending payment found for this ride.")

    if existing_payment.status == "paid":
        raise HTTPException(status_code=400, detail="Payment has already been completed for this ride.")

    if not ride.fare:  # Ensure fare is set before payment
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ride fare not set. Cannot process payment.")

    new_payment = models.Payment(
        ride_id=data.ride_id,
        user_id=current_user.id,
        amount_paid=ride.fare,
        payment_method=data.method,
        payment_date=datetime.utcnow(),
        status="paid"  # Or "pending" if you have a multi-step process
    )
    db.add(new_payment)

    # Update ride payment status
    ride.payment_status = "paid"
    db.add(ride)  # Add the updated ride to session
    db.commit()
    db.refresh(new_payment)
    db.refresh(ride)  # Refresh ride to reflect updated status

    return new_payment




