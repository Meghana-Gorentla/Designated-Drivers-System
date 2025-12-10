# routers/emergency.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.emergency import EmergencyContact
from app.models.user import User
from app.core.db import SessionLocal
from dependencies.auth import get_current_user

router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ContactCreate(BaseModel):
    name: str
    phone: str


@router.post("/add_emergency_contact")
def add_contact(
    data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = EmergencyContact(user_id=current_user.id, **data.dict())
    db.add(contact)
    db.commit()
    return {"message": "Emergency contact added."}



@router.get("/emergency_contacts")
def get_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contacts = db.query(EmergencyContact).filter(EmergencyContact.user_id == current_user.id).all()
    return contacts

