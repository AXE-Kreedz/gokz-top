import json
from datetime import datetime

from redis import asyncio as redis

EXPIRES_IN = 86400  # 24 hours
redis_client = redis.from_url("redis://localhost:6379", encoding="utf-8", decode_responses=True)


async def get_redis_conn():
    return redis_client


async def clear_cache():
    redis_ = await get_redis_conn()
    await redis_.flushdb()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
