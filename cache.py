# cache.py
import redis.asyncio as redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# create async redis client
redis_client = redis.from_url(REDIS_URL)

async def get_cache(key: str):
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def set_cache(key: str, value, expire: int = 300):
    await redis_client.set(key, json.dumps(value), ex=expire)

async def delete_cache(key: str):
    await redis_client.delete(key)
