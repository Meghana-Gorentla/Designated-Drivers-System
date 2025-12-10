from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str
    is_driver: bool
    gender: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: int
    name: Optional[str] = None  # <== allow null values
    email: Optional[str] = None
    phone: Optional[str]
    is_driver: Optional[bool]
    is_approved: Optional[bool] = None
    gender: Optional[str]

    class Config:
        from_attributes = True

class RideOut(BaseModel):
    id: int
    user_id: int
    driver_id: Optional[int]
    pickup_location: str
    drop_location: str
    status: str

    class Config:
        orm_mode = True


class PaymentOut(BaseModel):
    id: int
    ride_id: int
    amount: float
    method: str
    status: str
    recipient_id: int | None = None  # optional for admin to driver

    class Config:
        orm_mode = True