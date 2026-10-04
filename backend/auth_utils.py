from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings, get_database

from bson import ObjectId
import hashlib
bearer_scheme = HTTPBearer()




def hash_password(password: str) -> str:


    if not isinstance(password, str):
        raise ValueError("Password must be string")
    salt = b"mittika_secure_salt_2026"
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

def verify_password(plain: str, hashed: str) -> bool:
    if not isinstance(plain, str):
        return False
    return hash_password(plain) == hashed


def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return jwt.encode(
        {"sub": user_id, "exp": expire},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_database)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(401, "Invalid token")

    except JWTError:
        raise HTTPException(401, "Invalid token")

    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(401, "User not found")

    return user


async def get_artisan_user(current_user=Depends(get_current_user)):
    if current_user.get("userType") != "artisan":
        raise HTTPException(403, "Artisan access only")
    return current_user


async def get_shopper_user(current_user=Depends(get_current_user)):
    if current_user.get("userType") not in {"customer", "artisan"}:
        raise HTTPException(403, "Shopping access only")
    return current_user