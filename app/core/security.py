from passlib.context import CryptContext
import os
from datetime import datetime, timedelta, timezone
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str) -> str:
    secret = os.getenv("JWT_SECRET", "dev-secret")
    alg = os.getenv("JWT_ALG", "HS256")
    exp_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=alg)


def decode_token(token: str) -> dict:
    secret = os.getenv("JWT_SECRET", "dev-secret")
    alg = os.getenv("JWT_ALG", "HS256")
    return jwt.decode(token, secret, algorithms=[alg])