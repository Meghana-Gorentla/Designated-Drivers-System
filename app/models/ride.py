from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Float
from sqlalchemy.orm import relationship
from app.core.db import Base


class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    pickup_location = Column(String, nullable=False)
    drop_location = Column(String, nullable=False)
    status = Column(String, default="requested")
    fare = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rides", foreign_keys=[user_id])
    driver = relationship("User", back_populates="assigned_rides", foreign_keys=[driver_id])
