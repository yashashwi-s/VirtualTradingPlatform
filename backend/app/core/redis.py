import redis.asyncio as redis
from app.core.config import settings

# Redis client for caching
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class RedisCache:
    def __init__(self):
        self.client = redis_client
    
    async def get(self, key: str):
        """Get value from Redis cache"""
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, expire: int = 300):
        """Set value in Redis cache with expiration"""
        return await self.client.setex(key, expire, value)
    
    async def delete(self, key: str):
        """Delete key from Redis cache"""
        return await self.client.delete(key)
    
    async def exists(self, key: str):
        """Check if key exists in Redis cache"""
        return await self.client.exists(key)


# Global cache instance
cache = RedisCache()