from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, EmailStr, field_validator

from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.exceptions import UnauthorizedError


router = APIRouter()


# Temporary in-memory user store (we'll replace with DB later)
USERS: dict[str, str] = {}  # email -> hashed_password

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
def register(payload: RegisterRequest):
    email = payload.email.lower()

    if email in USERS:
        return {"status": "error", "message": "User already exists"}

    hashed = hash_password(payload.password)
    USERS[email] = hashed

    return {"status": "ok", "email": email}


@router.post("/login")
def login(payload: LoginRequest):
    email = payload.email.lower()

    hashed = USERS.get(email)
    if not hashed:
        return {"status": "error", "message": "Invalid credentials"}

    if not verify_password(payload.password, hashed):
        return {"status": "error", "message": "Invalid credentials"}

    token = create_access_token(email)
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