import redis.asyncio as redis
import json
from app.core.config import settings

redis_client: redis.Redis | None = None

async def init_redis():
    global redis_client
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )
    await redis_client.ping()
    print("Connected to Redis")

async def close_redis():
    if redis_client:
        await redis_client.close()

async def get_cached(key: str):
    if redis_client:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
    return None

async def set_cached(key: str, value, expire: int = 300):
    if redis_client:
        await redis_client.set(key, json.dumps(value), ex=expire)