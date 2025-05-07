import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://user:password@localhost:5432/task_manager")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
TOKEN_TTL = int(os.getenv("TOKEN_TTL", 3600))
TASK_CACHE_TTL = int(os.getenv("TASK_CACHE_TTL", 300))