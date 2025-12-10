from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.core.db import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ride_id = Column(Integer, ForeignKey("rides.id"))
    description = Column(Text)
    status = Column(String, default="pending")
