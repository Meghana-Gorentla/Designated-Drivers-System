# models/feedback.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.db import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(String)
