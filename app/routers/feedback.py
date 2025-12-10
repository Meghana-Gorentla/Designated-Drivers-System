# routers/feedback.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.feedback import Feedback
from app.models.ride import Ride
from app.core.db import SessionLocal
from app.models.user import User  # Assuming your User model is here
from dependencies.auth import get_current_user  # Update with actual path

router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class FeedbackCreate(BaseModel):
    ride_id: int
    rating: int
    comment: str


@router.post("/submit_feedback")
def submit_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ Authorization check: only drivers can submit feedback
    if current_user.is_driver:
        raise HTTPException(status_code=403, detail="Only users can submit feedback.")

    # ✅ Ride must exist
    ride = db.query(Ride).filter(Ride.id == data.ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")

    # ✅ Ride must be completed
    if ride.status != "completed":
        raise HTTPException(status_code=400, detail="Feedback can only be submitted for completed rides.")

    # ✅ Submit feedback
    feedback = Feedback(**data.dict())
    db.add(feedback)
    db.commit()

    return {"message": "Feedback submitted successfully."}
