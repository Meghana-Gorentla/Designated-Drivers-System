# app/main.py
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from app.core.db import engine
from app.models.user import Base
# Import the new user router
from app.routers import auth, ride, admin, complaint, emergency, feedback, earnings, payment, user # ADD 'user' here
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://127.0.0.1:5500", # Common for Live Server VS Code extension
    "http://localhost:5500", # Another common one
    "http://localhost:8000", # If you serve frontend from a simple python http server
    # Add the actual URL where your frontend will be served if it's different
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the API routers
app.include_router(auth.router)
app.include_router(ride.router, prefix="/rides", tags=["rides"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(feedback.router, tags=["feedback"])
app.include_router(emergency.router, tags=["emergency"])
app.include_router(earnings.router, tags=["earnings"])
app.include_router(complaint.router, tags=["complaints"])
app.include_router(payment.router, tags=["payments"])
# ADD the new user router
app.include_router(user.router, prefix="/users", tags=["users"])

