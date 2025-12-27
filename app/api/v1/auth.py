from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.exceptions import UnauthorizedError
from app.db.deps import get_db
from app.db.models import User

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 characters or fewer")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return {"status": "error", "message": "User already exists"}

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"status": "ok", "email": user.email}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"status": "error", "message": "Invalid credentials"}

    if not verify_password(payload.password, user.password_hash):
        return {"status": "error", "message": "Invalid credentials"}

    token = create_access_token(user.email)
    return {"status": "ok", "access_token": token, "token_type": "bearer"}


def get_current_user(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
        return payload["sub"]
    except Exception:
        raise UnauthorizedError("Invalid or expired token")


@router.get("/me")
def me(user: str = Depends(get_current_user)):
    return {"email": user}