from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from .schemas import UserCreate, TaskCreate, TaskUpdate, TaskOut, LoginData
from .crud import create_user, get_user_by_username, create_task, get_tasks, update_task
from .auth import verify_password, create_jwt_token
from .dependencies import get_current_user, redis_client
from .config import DATABASE_URL, TOKEN_TTL
from .models import User
import json
import asyncio

app = FastAPI()

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.post("/register")
async def register(user: UserCreate):
    existing_user = await get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = await create_user(user.username, user.password)
    return {"id": new_user.id, "username": new_user.username}

@app.post("/login")
async def login(login_data: LoginData):
    user = await get_user_by_username(login_data.username)
    if not user or not await verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt_token(user.id)
    await redis_client.set(f"token:{token}", user.id, ex=TOKEN_TTL)
    await redis_client.set(f"session:{user.id}", json.dumps({"username": user.username}), ex=TOKEN_TTL)
    return {"token": token}

@app.post("/tasks", response_model=TaskOut)
async def create_task_endpoint(task: TaskCreate, current_user: User = Depends(get_current_user)):
    new_task = await create_task(current_user, task.title, task.description, task.priority)
    return TaskOut.from_orm(new_task)

@app.get("/tasks", response_model=list[TaskOut])
async def get_tasks_endpoint(current_user: User = Depends(get_current_user)):
    return await get_tasks(current_user)

@app.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task_endpoint(task_id: int, task: TaskUpdate, current_user: User = Depends(get_current_user)):
    updated_task = await update_task(task_id, current_user, **task.dict())
    return TaskOut.from_orm(updated_task)

@app.on_event("startup")
async def startup_event():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("task_updates")
    asyncio.create_task(listen_for_updates(pubsub))

async def listen_for_updates(pubsub):
    async for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Received update: {message['data']}")