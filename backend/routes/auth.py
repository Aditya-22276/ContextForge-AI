from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.database import get_db
from models.user import User
from services.auth_service import hash_password, verify_password, create_access_token
import os

router = APIRouter()


# Request Schemas 

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleLoginRequest(BaseModel):
    token: str          # This is the id_token (JWT) from @react-oauth/google


# Register block

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=request.email,
        password_hash=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


# Login block

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


# Google Login


@router.post("/google-login")
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):

    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not google_client_id:
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: GOOGLE_CLIENT_ID not set"
        )

    #  Verifies the id_token with Google's public keys 
    #  google-auth handles clock skew, expiry, and audience checks.
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        idinfo = id_token.verify_oauth2_token(
            request.token,                  # the JWT string from the frontend
            google_requests.Request(),      # uses urllib3 under the hood
            google_client_id,              # must match aud claim in the JWT
            clock_skew_in_seconds=10       # tolerate small server clock drift
        )
    except ValueError as e:
        # verify_oauth2_token raises ValueError for any invalid token
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Google token verification failed: {str(e)}"
        )

    # Extracts verified claims
    email = idinfo.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    if not idinfo.get("email_verified", False):
        raise HTTPException(status_code=400, detail="Google email is not verified")

    #  Finds or create user 
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash="google_oauth_user"   # placeholder; never used for login
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    #  Issues your own JWT (same structure as normal login)
    access_token = create_access_token({"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}