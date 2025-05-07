import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_jwt_token(user_id: int) -> str:
    payload = {"sub": str(user_id)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)