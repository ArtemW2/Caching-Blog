import json
from uuid import UUID
from functools import wraps

from redis.asyncio import ConnectionError, Redis, ResponseError, TimeoutError

from src.application.interfaces import CacheStorage
from src.infrastructure.exceptions import (
    RedisConnectionError,
    RedisResponseError,
    RedisTimeoutError,
)

def cache_operation(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TimeoutError as e:
            raise RedisTimeoutError(e) from e
        except ConnectionError as e:
            raise RedisConnectionError(e) from e
        except ResponseError as e:
            raise RedisResponseError(e) from e
        
    return wrapper


class RedisCache(CacheStorage):
    def __init__(self, redis: Redis, ttl: int = 600) -> None:
        self.redis: Redis = redis
        self.ttl: int = ttl

    @cache_operation
    async def get(self, post_id: UUID) -> dict | None:
        data = await self.redis.get(str(post_id))
        return json.loads(data) if data else None
        
    @cache_operation
    async def set(self, post_id: UUID, post_dict: dict) -> None:
        await self.redis.setex(str(post_id), self.ttl, json.dumps(post_dict))
        
    @cache_operation
    async def invalidate(self, post_id: UUID) -> None:
        await self.redis.delete(str(post_id))
       