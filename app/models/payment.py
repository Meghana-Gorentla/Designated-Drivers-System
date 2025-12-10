from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.core.db import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))  # New field
    amount = Column(Float)
    method = Column(String)  # e.g., cash, UPI, card
    status = Column(String)  # e.g., pending, paid
