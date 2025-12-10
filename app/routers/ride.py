# app/routers/ride.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.core.db import SessionLocal
from app.models.ride import Ride
from app.models.user import User
from app.models.payment import Payment
from dependencies.auth import get_current_user

router = APIRouter() # This is correct, no prefix here

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_admin(user: User) -> bool:
    return user.email == "saimeghana.cd22@bmsce.ac.in"

def is_driver(user: User) -> bool:
    return user.is_driver

def is_customer(user: User) -> bool:
    return not user.is_driver

def calculate_fare(pickup: str, drop: str) -> float:
    base_fare = 50
    per_km_rate = 10
    estimated_distance_km = 5
    return base_fare + per_km_rate * estimated_distance_km

class RideRequest(BaseModel):
    pickup_location: str
    drop_location: str

@router.post("/request_ride")
def request_ride(
    data: RideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_customer(current_user):
        raise HTTPException(status_code=403, detail="Only customers can request rides.")
    if data.pickup_location==data.drop_location:
        raise HTTPException(status_code=400, detail="pickup and dropoff cant be same")

    fare = calculate_fare(data.pickup_location, data.drop_location)
    ride = Ride(
        user_id=current_user.id,
        driver_id=None,
        pickup_location=data.pickup_location,
        drop_location=data.drop_location,
        status="requested",
        fare=fare,
        timestamp=datetime.utcnow()
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)

    return {
        "ride_id": ride.id,
        "message": "Ride request submitted. Waiting for driver to accept.",
        "estimated_fare": fare
    }

class RideAccept(BaseModel):
    ride_id: int

@router.post("/accept_ride")
def accept_ride(
    data: RideAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_driver(current_user) or not current_user.is_approved:
        raise HTTPException(status_code=403, detail="Only approved drivers can accept rides.")

    active_ride = db.query(Ride).filter(
        Ride.driver_id == current_user.id,
        Ride.status.in_(["accepted", "ongoing"])
    ).first()
    if active_ride:
        raise HTTPException(status_code=400, detail="Driver already has an active ride.")

    ride = db.query(Ride).filter(Ride.id == data.ride_id).first()
    if not ride or ride.status != "requested":
        raise HTTPException(status_code=400, detail="Ride not available for acceptance.")

    ride.driver_id = current_user.id
    ride.status = "accepted"
    db.commit()

    return {"message": "Ride accepted by driver."}

@router.post("/start_ride")
def start_ride(
    ride_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride or ride.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized or ride not found.")
    if ride.status != "accepted":
        raise HTTPException(status_code=400, detail="Ride must be accepted first.")

    ride.status = "ongoing"
    db.commit()
    return {"message": "Ride status set to ongoing."}

class RideComplete(BaseModel):
    ride_id: int

@router.post("/complete_ride")
def complete_ride(
    data: RideComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ride = db.query(Ride).filter(Ride.id == data.ride_id).first()
    if not ride or ride.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized or ride not found.")
    if ride.status != "ongoing":
        raise HTTPException(status_code=400, detail="Only ongoing rides can be completed.")

    ride.status = "completed"
    payment = Payment(
        ride_id=ride.id,
        amount=ride.fare,
        method="cash",
        status="pending"
    )
    db.add(payment)
    db.commit()

    return {
        "message": "Ride marked as completed. Payment pending.",
        "fare": ride.fare
    }

@router.get("/ride_status") # <-- CHANGE THIS
def get_ride_status(
    ride_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    if not is_admin(current_user) and current_user.id not in [ride.user_id, ride.driver_id]:
        raise HTTPException(status_code=403, detail="Not authorized.")

    return ride

@router.post("/cancel_ride") # <-- CHANGE THIS
def cancel_ride(
    ride_id: int,
    cancelled_by: str = Query(..., regex="^(user|driver)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")

    if cancelled_by == "user" and current_user.id != ride.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized.")
    if cancelled_by == "driver" and current_user.id != ride.driver_id:
        raise HTTPException(status_code=403, detail="Unauthorized.")

    if ride.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Ride cannot be cancelled.")

    ride.status = "cancelled"
    db.commit()

    return {"message": f"Ride cancelled by {cancelled_by}."}

@router.get("/notify_status_change") # <-- CHANGE THIS
def notify_status_change(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride or current_user.id not in [ride.user_id, ride.driver_id] and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Unauthorized or ride not found.")

    return {
        "message": f"Notified relevant parties about status change: {ride.status}",
        "ride_id": ride.id,
        "status": ride.status
    }


@router.get("/user/{user_id}/rides") # <-- CHANGE THIS
def get_user_rides(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Allow access if current user is not a driver and is requesting their own rides or if admin
    if current_user.is_driver:
        raise HTTPException(status_code=403, detail="Drivers cannot access user rides.")

    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Unauthorized access to user rides.")

    rides = db.query(Ride).filter(Ride.user_id == user_id).all()
    return rides


@router.get("/driver/{driver_id}/rides") # <-- CHANGE THIS
def get_driver_rides(driver_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Allow access if current user is the driver or if admin
    if not current_user.is_driver and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Unauthorized access to driver rides.")

    # Optionally, you might want to check if the requested driver_id matches current_user.id
    # to prevent a driver from viewing other drivers' rides, if needed:
    if current_user.is_driver and current_user.id != driver_id:
        raise HTTPException(status_code=403, detail="Drivers can only access their own rides.")

    rides = db.query(Ride).filter(Ride.driver_id == driver_id).all()
    return rides


@router.get("/driver/requested", status_code=200) # <-- THIS IS THE KEY CHANGE FOR /rides/requested
def get_all_requested_rides(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Allow only admin or approved drivers to access
    if not (is_admin(current_user) or (current_user.is_driver and current_user.is_approved)):
        raise HTTPException(status_code=403, detail="Only approved drivers or admin can view requested rides.")

    requested_rides = db.query(Ride).filter(Ride.status == "requested").all()
    return requested_rides