from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt_sha256", "bcrypt"],  # ✅ pbkdf2 avoids bcrypt crash
    deprecated="auto",
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False

def create_access_token(subject: str) -> str:
    secret = settings.JWT_SECRET
    alg = settings.JWT_ALG
    exp_minutes = settings.JWT_EXPIRE_MINUTES

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=alg)

def decode_token(token: str) -> dict:
    secret = settings.JWT_SECRET
    alg = settings.JWT_ALG
    return jwt.decode(token, secret, algorithms=[alg])