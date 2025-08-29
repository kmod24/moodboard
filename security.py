# security.py
import time
import bcrypt
import jwt
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError
from fastapi import HTTPException
from config import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def create_jwt(user_id: int, ttl_seconds: int = 60 * 60 * 24) -> str:
    payload = {
        "sub": str(user_id),                         # <-- must be STRING
        "exp": int(time.time()) + ttl_seconds,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def decode_jwt(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return int(payload["sub"])                   # <-- cast back to int
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except (InvalidSignatureError, DecodeError):
        raise HTTPException(status_code=401, detail="Invalid token")
