import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.exceptions import DoesNotExist
from .auth import create_jwt_token
from .models import User
from .config import TOKEN_TTL, REDIS_URL
import logging
import jwt
from .config import SECRET_KEY, ALGORITHM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await User.get(id=int(user_id))
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except DoesNotExist:
        raise HTTPException(status_code=401, detail="User not found")