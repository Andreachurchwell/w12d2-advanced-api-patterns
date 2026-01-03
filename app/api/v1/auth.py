from fastapi import APIRouter, Depends, Header, Request, HTTPException, Response
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.exceptions import UnauthorizedError
from app.core.redis_client import rate_limit_info
from app.db.deps import get_db
from app.db.models import User
import time
from fastapi.responses import JSONResponse

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
            raise ValueError("Password must be 72 bytes or fewer")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_len(cls, v: str):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer")
        return v


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
async def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):

    ip = request.client.host if request.client else "unknown"
    key = f"rl:login:{ip}"

    try:
        info = await rate_limit_info(key=key, limit=5, window_seconds=60)

        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])

        if info["is_limited"]:
            headers = {
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset"]),
                "Retry-After": str(max(1, info["reset"] - int(time.time()))),
            }
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many login attempts. Try again in a minute."},
                headers=headers,
            )


    except HTTPException:
        raise
    except Exception:
        # Redis not available → skip rate limiting for now
        pass

    email = payload.email.lower()

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.email)
    return {"status": "ok", "access_token": token, "token_type": "bearer"}



def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()

    try:
        payload = decode_token(token)
        email = payload["sub"].lower()
    except Exception:
        raise UnauthorizedError("Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise UnauthorizedError("User not found")

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise UnauthorizedError("Admin access required")
    return user

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"email": user.email, "role": user.role}
