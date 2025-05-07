from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=128)

    @classmethod
    async def get_by_username(cls, username: str):
        try:
            return await cls.get(username=username)
        except DoesNotExist:
            return None

class Task(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="tasks")
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    status = fields.CharField(max_length=20, default="pending")
    priority = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)