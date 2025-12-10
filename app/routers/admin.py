from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.db import SessionLocal # your session dependency
from app.models.complaint import Complaint
from app.models.payment import Payment
from app.models.ride import Ride
from app.models.user import User  # your SQLAlchemy model
from app.schemas.user import UserOut, RideOut, PaymentOut  # pydantic model for response
from dependencies.auth import get_current_user

router = APIRouter()

# Hardcoded admin email
ADMIN_EMAIL = "saimeghana.cd22@bmsce.ac.in"


class AdminApprovalRequest(BaseModel):
    admin_email: str
    driver_id : int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/admin/approve_driver")
def approve_driver(request: AdminApprovalRequest, db: Session = Depends(get_db)):
    # Check if the admin email is correct
    if request.admin_email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Unauthorized: Only admin can approve drivers.")

    # Check if driver exists
    driver = db.query(User).filter(User.id == request.driver_id, User.is_driver == True).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")

    # Approve the driver
    driver.is_approved = True
    db.commit()

    return {"message": f"Driver with ID {request.driver_id} has been approved."}
# routers/users.py (or wherever you keep your user routes)


@router.get("/users/drivers", response_model=List[UserOut])
def get_all_drivers(admin_email: str = Query(...), db: Session = Depends(get_db)):
    if admin_email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return db.query(User).filter(User.is_driver == True).all()


@router.get("/users/customers", response_model=List[UserOut])
def get_customers(admin_email: str = Query(...), db: Session = Depends(get_db)):
    if admin_email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Unauthorized")
    customers = db.query(User).filter(User.is_driver == False).all()
    return customers


class AdminPaymentCreate(BaseModel):
    ride_id: int
    driver_id: int
    amount: float
    method: str  # e.g., bank_transfer, UPI

@router.post("/admin/pay_driver")
def pay_driver(data: AdminPaymentCreate, db: Session = Depends(get_db)):
    ride = db.query(Ride).filter(Ride.id == data.ride_id).first()
    if not ride or ride.driver_id != data.driver_id:
        raise HTTPException(status_code=400, detail="Invalid ride or driver.")

    payment = Payment(
        ride_id=data.ride_id,
        recipient_id=data.driver_id,
        amount=data.amount,
        method=data.method,
        status="paid"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment to driver successful.",
        "payment_id": payment.id,
        "status": payment.status
    }

@router.get("/admin/complaints")
def view_complaints(request: AdminApprovalRequest,db: Session = Depends(get_db)):
    # Check if the admin email is correct
    if request.admin_email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Unauthorized: Only admin can approve drivers.")
    complaints = db.query(Complaint).all()
    return complaints


@router.get("/admin/all_users", response_model=List[UserOut])
def get_all_users(admin_email: str = Query(...), db: Session = Depends(get_db)):
    if admin_email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return db.query(User).all()


@router.get("/admin/all_rides", response_model=List[RideOut])
def get_all_rides(admin_email: str = Query(...), db: Session = Depends(get_db)):
    if admin_email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return db.query(Ride).all()


@router.get("/admin/all_payments", response_model=List[PaymentOut])
def get_all_payments(admin_email: str = Query(...), db: Session = Depends(get_db)):
    if admin_email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return db.query(Payment).all()