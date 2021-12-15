from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Tells(Model):
    id = fields.UUIDField(pk=True)
    text = fields.TextField()
    has_image = fields.BooleanField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class PydanticMeta:
        ordering = "created_at"


TellResponse = pydantic_model_creator(Tells, name="Tell")
