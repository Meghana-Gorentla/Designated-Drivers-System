from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.core.db import SessionLocal, Base
from app.models.complaint import Complaint
from app.models.ride import Ride
from app.models.user import User
from app.models.payment import Payment
from app.routers.ride import is_customer
from dependencies.auth import get_current_user


class ComplaintCreate(BaseModel):
    user_id: int
    ride_id: int
    description: str

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/complaints")
def submit_complaint(data: ComplaintCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if not is_customer(current_user):
        raise HTTPException(status_code=403, detail="This collects only customers complaints, Drivers can complain to 'saimeghana.cd22@bmsce.ac.in'.")
    complaint = Complaint(
        user_id=data.user_id,
        ride_id=data.ride_id,
        description=data.description
    )
    ride = db.query(Ride).filter(Ride.id == data.ride_id).first()
    if not ride:
        raise HTTPException(status_code=403, detail="Ride not found to complain.")
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return {"message": "Complaint submitted successfully.", "complaint_id": complaint.id}


