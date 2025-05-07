import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.exceptions import DoesNotExist
from .auth import create_jwt_token
from .models import User
from .config import TOKEN_TTL, REDIS_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user_id = await redis_client.get(f"token:{token}")
        if not user_id:
            logger.error(f"Token not found in Redis: {token}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Получаем пользователя по ID
        try:
            user = await User.get(id=int(user_id))
            return user
        except DoesNotExist:
            logger.error(f"User not found for ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )