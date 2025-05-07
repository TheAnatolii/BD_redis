import json
from tortoise.exceptions import DoesNotExist
from .models import User, Task
from .schemas import TaskOut
from .auth import get_password_hash
from .config import TOKEN_TTL, TASK_CACHE_TTL
from .dependencies import redis_client
import logging

logger = logging.getLogger(__name__)

async def create_user(username: str, password: str):
    try:
        hashed_password = await get_password_hash(password)
        user = await User.create(username=username, password_hash=hashed_password)
        logger.info(f"Created user: {username} with password hash: {user.password_hash}")
        return user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise

async def get_user_by_username(username: str):
    try:
        user = await User.get(username=username)
        logger.info(f"Retrieved user: {user.username}")
        return user
    except DoesNotExist:
        logger.info(f"User not found: {username}")
        return None
    return await User.get_by_username(username)

async def create_task(user: User, title: str, description: str, priority: int):
    task = await Task.create(user=user, title=title, description=description, priority=priority)
    try:
        await redis_client.delete(f"tasks:{user.id}")
        await redis_client.publish("task_updates", f"New task: {title}")
    except redis.RedisError as e:
        logger.error(f"Redis error: {str(e)}")
    return task

async def get_tasks(user: User) -> list[TaskOut]:
    try:
        cached_tasks = await redis_client.get(f"tasks:{user.id}")
        if cached_tasks:
            return [TaskOut(**task) for task in json.loads(cached_tasks)]
    except redis.RedisError:
        pass  # Fallback to database
    tasks = await Task.filter(user=user).values("id", "title", "description", "status", "priority")
    task_list = [TaskOut(**task) for task in tasks]
    try:
        await redis_client.set(f"tasks:{user.id}", json.dumps([task.dict() for task in task_list]), ex=TASK_CACHE_TTL)
    except redis.RedisError:
        pass  # Log error but continue
    return task_list

async def update_task(task_id: int, user: User, **kwargs):
    task = await Task.get(id=task_id, user=user)
    for key, value in kwargs.items():
        if value is not None:
            setattr(task, key, value)
    await task.save()
    try:
        await redis_client.delete(f"tasks:{user.id}")
        await redis_client.publish("task_updates", f"Task updated: {task.title}")
    except redis.RedisError as e:
        logger.error(f"Redis error: {str(e)}")
    return task