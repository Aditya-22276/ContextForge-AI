from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.database import get_db
from models.user import User
from services.auth_service import hash_password, verify_password, create_access_token
from google.oauth2 import id_token
from google.auth.transport import requests
import os

router = APIRouter()


# REQUEST SCHEMAS
class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# REGISTER
@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(request.password)

    new_user = User(
        email=request.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# LOGIN
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    # 🔥 IMPORTANT: INCLUDE user_id
    token = create_access_token({
        "user_id": user.id
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/google-login")
def google_login(data: dict, db: Session = Depends(get_db)):

    token = data.get("token")

    try:

        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            os.getenv("GOOGLE_CLIENT_ID")
        )

        email = idinfo["email"]

        user = db.query(User).filter(
            User.email == email
        ).first()

        # Create user automatically if not exists
        if not user:

            user = User(
                email=email,
                password_hash="google_oauth_user"
            )

            db.add(user)
            db.commit()
            db.refresh(user)

        # SAME TOKEN STRUCTURE AS NORMAL LOGIN
        access_token = create_access_token({
            "user_id": user.id
        })

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )