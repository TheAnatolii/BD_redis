from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    password: str

class LoginData(BaseModel):
    username: str
    password: str

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: int

    model_config = ConfigDict(from_attributes=True)