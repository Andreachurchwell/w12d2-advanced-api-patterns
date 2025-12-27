from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, field_validator
from app.core.security import hash_password


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
def register(payload: RegisterRequest):
    # print("PW bytes:", len(payload.password.encode("utf-8")))
    hashed = hash_password(payload.password)
    return {
        "status": "ok",
        "email": payload.email,
        "password_hashed_preview": hashed[:20]  # (temporary)
    }


@router.post("/login")
def login(payload: LoginRequest):
    return {
        "status": "ok",
        "email": payload.email
    }