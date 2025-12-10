from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_driver = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)  # for drivers
    gender = Column(String)  # male, female, other
    driver_license = Column(String, nullable=True)  # New: License field for drivers

    rides = relationship("Ride", back_populates="user", foreign_keys="[Ride.user_id]")  # For customers
    assigned_rides = relationship("Ride", back_populates="driver", foreign_keys="[Ride.driver_id]")  # For drivers

