import os

TORTOISE_ORM = {
    "connections": {"default": os.getenv("DB_URL")},
    "apps": {"models": {"models": ["aerich.models", "models.tells"]}},
}
